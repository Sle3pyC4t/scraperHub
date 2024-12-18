from abc import ABC
from time import sleep

from selenium.common import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver

from scrapers.abstract_scraper import AbstractScraper

LISTING_ANNOUNCEMENTS_URL = ("https://www.binance.com/en/support/"
                             "announcement/new-cryptocurrency-listing?c=48&navId=48&hl=en")
LOADING_INTERVAL = 0.5


class BinanceListingAnnouncementsScraper(AbstractScraper, ABC):
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.latest_announcement_link = None
        self.announcement_list = []

    def authenticate(self):
        pass

    def scrape(self):
        """
        Get all listing announcements id from the website
        :return:
        """
        self.driver.get(LISTING_ANNOUNCEMENTS_URL)
        sleep(LOADING_INTERVAL)
        try:
            self.driver.find_element('xpath', '//*[@id="binance_hk_compliance_popup_proceed"]').click()
        except NoSuchElementException:
            pass
        sleep(LOADING_INTERVAL)
        for i in range(1, 21):
            try:
                announcement_element = (
                    self.driver.find_element('xpath', f'//*[@id="app-wrap"]/div[2]/div[2]/div[2]/section/div/div[1]/div[{i}]/a'))
                self.announcement_list.append(announcement_element.get_attribute('href'))
            except NoSuchElementException:
                break
        # get link address from first announcement
        if len(self.announcement_list) == 0:
            raise Exception("No announcement found")
        self.latest_announcement_link = self.announcement_list[0]

    def export_data(self):
        pass

