"""
Abstract scraper class for all scrapers
"""

from abc import ABC, abstractmethod

class AbstractScraper(ABC):
    """
    Abstract class for all scrapers
    """
    @abstractmethod
    def __init__(self):
        """
        Abstract method to initialize the scraper
        """
        pass

    @abstractmethod
    def authenticate(self):
        """
        Method to authenticate the scraper
        """
        pass

    @abstractmethod
    def scrape(self):
        """
        Abstract method to scrape data from the website
        """
        pass

    @abstractmethod
    def export_data(self):
        """
        Abstract method to export the scraped data
        """
        pass