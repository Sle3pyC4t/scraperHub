from selenium.webdriver.firefox.webdriver import WebDriver

from scrapers.abstract_scraper import AbstractScraper
from abc import ABC


class AnnouncementContent(AbstractScraper, ABC):
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.title = ""
        self.time = ""
        self.content = ""

    def authenticate(self):
        pass

    def scrape(self, url: str = ""):
        self.driver.get(url)
        self.content = self.driver.find_element('xpath', '//*[@id="app-wrap"]/div/div[2]/div/div[2]/div')
        self.title = self.driver.find_element('xpath', '//*[@id="app-wrap"]/div/div[2]/div/div[2]/div/h1').text
        self.time = self.driver.find_element('xpath', '//*[@id="app-wrap"]/div/div[2]/div/div[2]/div/div[2]').text

    def export_data(self):
        pass