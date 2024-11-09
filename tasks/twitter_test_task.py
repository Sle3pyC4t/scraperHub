import sys

import toml

import webdrivers.firefox
from scrapers.twitter.scrapper import TwitterScrapper


def test_twitter_scraper():
    driver = webdrivers.firefox.get_firefox()
    driver.maximize_window()
    config = toml.load("../config.toml")
    scraper = TwitterScrapper(driver, "",
                              config.get("twitter").get("username"),
                              config.get("twitter").get("password")
                              )
    config.clear()
    scraper.authenticate()
    scraper.scrape(scrape_query="Bitcoin from:elonmusk", max_tweets=100)
    scraper.export_data()
    driver.close()


if __name__ == "__main__":
    test_twitter_scraper()
