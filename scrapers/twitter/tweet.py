from time import sleep
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains


class Tweet:
    def __init__(self, card: WebDriver, driver: WebDriver, actions: ActionChains, scrape_poster_details=False) -> None:
        self.card = card
        self.user = self.get_element_text('.//div[@data-testid="User-Name"]//span')
        self.handle = self.get_element_text('.//span[contains(text(), "@")]')
        self.date_time = self.get_element_attribute(".//time", "datetime")
        self.is_ad = self.date_time is None
        self.verified = self.is_element_present('.//*[local-name()="svg" and @data-testid="icon-verified"]')
        self.content = self.get_tweet_content()
        self.reply_cnt = self.get_count('.//button[@data-testid="reply"]//span')
        self.retweet_cnt = self.get_count('.//button[@data-testid="retweet"]//span')
        self.like_cnt = self.get_count('.//button[@data-testid="like"]//span')
        self.analytics_cnt = self.get_count('.//a[contains(@href, "/analytics")]//span')
        self.tags = self.get_elements_text('.//a[contains(@href, "src=hashtag_click")]')
        self.mentions = self.get_elements_text('.//div[@data-testid="tweetText"]//a[contains(text(), "@")]')
        self.emojis = self.get_emojis()
        self.profile_img = self.get_element_attribute('.//div[@data-testid="Tweet-User-Avatar"]//img', "src")
        self.tweet_link = self.get_element_attribute(".//a[contains(@href, '/status/')]", "href")
        self.tweet_id = self.tweet_link.split("/")[-1] if self.tweet_link else ""

        self.following_cnt = self.followers_cnt = "0"
        self.user_id = None

        if scrape_poster_details:
            self.scrape_user_details(driver, actions)

        self.tweet = (
            self.user, self.handle, self.date_time, self.verified, self.content, self.reply_cnt,
            self.retweet_cnt, self.like_cnt, self.analytics_cnt, self.tags, self.mentions,
            self.emojis, self.profile_img, self.tweet_link, self.tweet_id, self.user_id,
            self.following_cnt, self.followers_cnt
        )

    def get_element_text(self, xpath: str, default="skip") -> str:
        return self._get_element(self.card, xpath, default, "text")

    def get_element_attribute(self, xpath: str, attribute: str, default="skip") -> str:
        return self._get_element(self.card, xpath, default, "attribute", attribute)

    def is_element_present(self, xpath: str) -> bool:
        try:
            self.card.find_element("xpath", xpath)
            return True
        except NoSuchElementException:
            return False

    def get_tweet_content(self) -> str:
        return "".join(
            element.text for element in self.card.find_elements("xpath", '(.//div[@data-testid="tweetText"])[1]//span | (.//div[@data-testid="tweetText"])[1]//a')
        )

    def get_count(self, xpath: str) -> str:
        return self._get_element(self.card, xpath, "0", "text")

    def get_elements_text(self, xpath: str) -> list:
        return [element.text for element in self.card.find_elements("xpath", xpath)]

    def get_emojis(self) -> list:
        return [
            emoji.get_attribute("alt").encode("unicode-escape").decode("ASCII")
            for emoji in self.card.find_elements("xpath", '(.//div[@data-testid="tweetText"])[1]//img[contains(@src, "emoji")]')
        ]

    def scrape_user_details(self, driver, actions: ActionChains):
        el_name = self.card.find_element("xpath", './/div[@data-testid="User-Name"]//span')
        for _ in range(3):
            try:
                actions.move_to_element(el_name).perform()
                hover_card = driver.find_element("xpath", '//div[@data-testid="hoverCardParent"]')
                self.user_id = self._get_element(hover_card, '(.//div[contains(@data-testid, "-follow")]) | (.//div[contains(@data-testid, "-unfollow")])', None, "attribute", "data-testid").split("-")[0]
                self.following_cnt = self._get_element(hover_card, './/a[contains(@href, "/following")]//span', "0", "text")
                self.followers_cnt = self._get_element(hover_card, './/a[contains(@href, "/verified_followers")]//span', "0", "text")
                break
            except (NoSuchElementException, StaleElementReferenceException):
                sleep(0.5)

    def _get_element(self, card, xpath: str, default, mode: str, attribute=None):
        try:
            element = card.find_element("xpath", xpath)
            return element.get_attribute(attribute) if mode == "attribute" else element.text
        except NoSuchElementException:
            return default
