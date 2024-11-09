import sys

from fake_headers import Headers
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
)
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from utils.logger import logger


def get_firefox(
        headless: bool = False,
        proxy: str = None
):
    logger.info("Setup WebDriver...")
    header = Headers().generate()["User-Agent"]
    browser_option = FirefoxOptions()
    browser_option.add_argument("--no-sandbox")
    browser_option.add_argument("--disable-dev-shm-usage")
    browser_option.add_argument("--ignore-certificate-errors")
    browser_option.add_argument("--disable-gpu")
    browser_option.add_argument("--log-level=3")
    browser_option.add_argument("--disable-notifications")
    browser_option.add_argument("--disable-popup-blocking")
    browser_option.add_argument("--user-agent={}".format(header))
    if proxy is not None:
        browser_option.add_argument("--proxy-server=%s" % proxy)

    if headless:
        browser_option.add_argument("--headless")

    try:
        logger.info("Initializing FirefoxDriver...")
        driver = webdriver.Firefox(
            options=browser_option,
        )

        logger.info("WebDriver Setup Complete")
        return driver
    except WebDriverException:
        try:
            logger.info("Downloading FirefoxDriver...")
            firefoxdriver_path = GeckoDriverManager().install()
            firefox_service = FirefoxService(executable_path=firefoxdriver_path)
            logger.info("Initializing FirefoxDriver...")
            driver = webdriver.Firefox(
                service=firefox_service,
                options=browser_option,
            )
            logger.info("WebDriver Setup Complete")
            return driver
        except Exception as e:
            logger.info(f"Error setting up WebDriver: {e}")
            sys.exit(1)


if __name__ == "__main__":
    driver = get_firefox()
    driver.maximize_window()
    driver.get("https://google.com")
    driver.close()
