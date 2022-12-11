"""This module contains the UdemyDriver class."""
from __future__ import annotations

from collections.abc import Callable
from logging import getLogger
from multiprocessing import JoinableQueue as MpQueue

import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome

from udemy_autocoupons.constants import (
    PROFILE_DIRECTORY,
    USER_DATA_DIR,
    WAIT_POLL_FREQUENCY,
    WAIT_TIMEOUT,
)
from udemy_autocoupons.udemy_course import UdemyCourse

_printer = getLogger('printer')
_debug = getLogger('debug')


class UdemyDriver:
    """Handles Udemy usage.

    Requires the profile set in PROFILE_DIRECTORY in USER_DATA_DIR to already be
    logged into the Udemy Account.

    """

    def __init__(self) -> None:
        """Starts the driver."""
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')

        options.add_argument(f'--profile-directory={PROFILE_DIRECTORY}')
        options.add_argument(f'user-data-dir={USER_DATA_DIR}')

        _debug.debug(
            'Starting WebDriver with --profile-directory %s and user-data-dir %s',
            PROFILE_DIRECTORY,
            USER_DATA_DIR,
        )

        self.driver = uc.Chrome(options=options)

        _debug.debug('Started WebDriver')

        self._wait = WebDriverWait(
            self.driver,
            WAIT_TIMEOUT,
            WAIT_POLL_FREQUENCY,
        )

    def enroll_from_queue(self, mp_queue: MpQueue[UdemyCourse | None]) -> None:  # pylint: disable=unsubscriptable-object
        """Enrolls in all courses in a queue.

        When a None is received from the queue, it is considered that there
        won't be any more courses.

        Args:
            mp_queue: A multiprocessing queue with courses.

        """
        while course := mp_queue.get():
            self.enroll(course)

            qsize = mp_queue.qsize()
            _printer.info('%s courses left.', qsize)
            _debug.debug('Enroll finished for %s. qsize is %s', course, qsize)

            mp_queue.task_done()

        _debug.debug('Got None in multiprocessing queue')

        mp_queue.task_done()

    def enroll(self, course: UdemyCourse) -> None:
        """If the course is discounted, it enrolls the account in it.

        Args:
            course: The course to enroll in.

        """
        try:
            self._enroll(course)
        except WebDriverException:
            _debug.exception(
                'A WebDriverException was encountered while enrolling in %s',
                course,
            )
            _printer.error('An error occurred while enrolling, skipping course')

    def _enroll(self, course: UdemyCourse) -> None:
        url = f'https://www.udemy.com/course/{course.url_id}/?couponCode={course.coupon}'

        _debug.debug('Enrolling in %s', url)

        self.driver.get(url)

        # This shows even if the course is not discounted, so it's a safe wait
        enroll_button = self._wait_for_clickable(
            '[data-purpose*="buy-this-course-button"]',
        )

        if not self._current_course_is_discounted():
            _debug.debug('_course_is_discounted returned False')
            return

        enroll_button.click()

        if not self._checkout_is_correct():
            _debug.debug('_checkout_is_correct returned False')
            return

        checkout_button = self._wait_for_clickable(
            '[class*="checkout-button--checkout-button--button"]',
        )
        checkout_button.click()

        self._wait.until(lambda driver: 'checkout' not in driver.current_url)

    def quit(self) -> None:
        """Quits the WebDriver instance."""
        self.driver.quit()

    def _current_course_is_discounted(self) -> bool:
        """Check if the course currently on screen is discounted.

        A course is considered discounted if it's not always free, it's not
        already purchased and currently it's free temporarily.

        Returns:
            True if the course is discounted, False otherwise

        """
        purchased_selector = '[class*="purchase-info"]'
        price_selector = '[data-purpose*="course-price-text"] span:not(.ud-sr-only)'
        free_badge_selector = '.ud-badge-free'

        self._wait.until(
            EC.any_of(
                self._ec_located(purchased_selector),
                self._ec_located(price_selector),
                self._ec_located(free_badge_selector),
            ),
        )

        return (
            not self._find_elements(purchased_selector) and
            not self._find_elements(free_badge_selector) and
            '$' not in self._find_elements(price_selector)[0].text
        )

    def _checkout_is_correct(self) -> bool:
        """Checks that the screen is a checkout and the course is free.

        This is a fallback in case _current_course_is_discounted returns a false
        positive.

        Returns:
            True if the checkout is correct, False otherwise.

        """
        total_amount_locator = '[data-purpose*="total-amount-summary"] span:nth-child(2)'

        self._wait.until(
            EC.any_of(
                EC.url_contains('/learn/lecture/'),
                EC.url_contains('/cart/subscribe/course/'),
                self._ec_located(total_amount_locator),
            ),
        )

        if '/cart/checkout/express/course/' not in self.driver.current_url:
            return False

        return self._wait_for(total_amount_locator).text.startswith('0')

    def _wait_for(self, css_selector: str) -> WebElement:
        return self._wait.until(self._ec_located(css_selector))

    def _wait_for_clickable(self, css_selector: str) -> WebElement:
        return self._wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)),
        )

    def _find(self, css_selector: str) -> WebElement:
        return self.driver.find_element(By.CSS_SELECTOR, css_selector)

    def _find_elements(self, css_selector: str) -> list[WebElement]:
        return self.driver.find_elements(By.CSS_SELECTOR, css_selector)

    @staticmethod
    def _ec_located(css_selector: str) -> Callable[[Chrome], WebElement]:
        return EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
