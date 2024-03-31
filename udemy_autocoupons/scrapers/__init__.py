"""This package contains all scrapers."""

from udemy_autocoupons.scrapers.web_scrappers.freebiesglobal_scraper import (
    FreebiesGlobalScraper,
)
from udemy_autocoupons.scrapers.web_scrappers.freshcoupons_scraper import FreshcouponsScraper
from udemy_autocoupons.scrapers.web_scrappers.telegram_scraper import TelegramScraper
from udemy_autocoupons.scrapers.web_scrappers.tutorialbar_scraper import TutorialbarScraper

scraper_types = (
    TutorialbarScraper,
    FreebiesGlobalScraper,
    TelegramScraper,
    FreshcouponsScraper,
)

ScrapersT = tuple[
    TutorialbarScraper,
    FreebiesGlobalScraper,
    TelegramScraper,
    FreshcouponsScraper,
]
