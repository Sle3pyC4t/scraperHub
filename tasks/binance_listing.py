import sys
from time import sleep

import toml

import webdrivers.firefox
from scrapers.binance.listing_announcements import BinanceListingAnnouncementsScraper
from utils.logger import logger


def telegram_notice(link):
    """
    TODO: Send a Telegram notice
    :param link:
    :return:
    """
    logger.info("Sending Telegram Notice...")


def is_valid_listing(link):
    """
    TODO: If the content contains valuable listing info
    :param link:
    :return:
    """
    logger.info("Checking Content...")
    return True


def binance_listing():
    driver = webdrivers.firefox.get_firefox()
    driver.maximize_window()
    scraper = BinanceListingAnnouncementsScraper(driver)
    scraper.scrape()
    latest_link = scraper.latest_announcement_link
    while True:
        logger.info("Latest Link: " + latest_link)
        sleep(10)
        scraper.scrape()
        current_latest_link = scraper.latest_announcement_link
        if current_latest_link != latest_link:
            latest_link = current_latest_link
            if not is_valid_listing(latest_link):
                continue
            telegram_notice(latest_link)


if __name__ == "__main__":
    binance_listing()
