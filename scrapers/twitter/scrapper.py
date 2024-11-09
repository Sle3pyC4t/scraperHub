import os
import sys
from abc import ABC
from datetime import datetime
from time import sleep

import pandas as pd
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains, Keys

from scrapers.abstract_scraper import AbstractScraper
from scrapers.twitter.progress import Progress
from scrapers.twitter.tweet import Tweet
from utils.logger import logger
from utils.scroller import Scroller

TWITTER_LOGIN_URL = "https://twitter.com/i/flow/login"

class TwitterScrapper(AbstractScraper, ABC):
    def __init__(self, driver, mail, username, password, max_tweets=50, scrape_username=None, scrape_hashtag=None, scrape_query=None, scrape_poster_details=False, scrape_latest=True, scrape_top=False):
        logger.info("Initializing Twitter Scraper...")
        self.driver = driver
        self.mail = mail
        self.username = username
        self.password = password
        self.max_tweets = max_tweets
        self.progress = Progress(0, max_tweets)
        self.actions = ActionChains(self.driver)
        self.scroller = Scroller(self.driver)
        self._config_scraper(max_tweets, scrape_username, scrape_hashtag, scrape_query, scrape_latest, scrape_top, scrape_poster_details)

    def authenticate(self):
        logger.info("Logging in to Twitter...")
        try:
            self.driver.maximize_window()
            self.driver.get(TWITTER_LOGIN_URL)
            sleep(3)
            self._input_username()
            self._input_unusual_activity()
            self._input_password()
            auth_token = next((cookie["value"] for cookie in self.driver.get_cookies() if cookie["name"] == "auth_token"), None)
            if auth_token is None:
                raise ValueError("Authentication failed. Please check your credentials and try again.")
            logger.info("Login Successful")
        except Exception as e:
            logger.info(f"Login Failed: {e}")
            sys.exit(1)

    def scrape(self, max_tweets=50, no_tweets_limit=False, scrape_username=None, scrape_hashtag=None, scrape_query=None, scrape_latest=True, scrape_top=False, scrape_poster_details=False, router=None):
        self._config_scraper(max_tweets, scrape_username, scrape_hashtag, scrape_query, scrape_latest, scrape_top, scrape_poster_details)
        router = router or self.router
        router()
        logger.info(f"Scraping Tweets from {self.scraper_details['type']}...")

        try:
            self.driver.find_element("xpath", "//span[text()='Refuse non-essential cookies']/../../..").click()
        except NoSuchElementException:
            pass

        self.progress.print_progress(0, False, 0, no_tweets_limit)
        refresh_count = empty_count = retry_cnt = 0

        while self.scroller.scrolling:
            try:
                self.get_tweet_cards()
                added_tweets = 0

                for card in self.tweet_cards[-15:]:
                    try:
                        tweet_id = str(card)
                        if tweet_id not in self.tweet_ids:
                            self.tweet_ids.add(tweet_id)
                            if not self.scraper_details["poster_details"]:
                                self.driver.execute_script("arguments[0].scrollIntoView();", card)
                            tweet = Tweet(card=card, driver=self.driver, actions=self.actions, scrape_poster_details=self.scraper_details["poster_details"])
                            if tweet and tweet.tweet and not tweet.is_ad:
                                self.data.append(tweet.tweet)
                                added_tweets += 1
                                self.progress.print_progress(len(self.data), False, 0, no_tweets_limit)
                                if len(self.data) >= self.max_tweets and not no_tweets_limit:
                                    self.scroller.scrolling = False
                                    break
                    except NoSuchElementException:
                        continue

                if len(self.data) >= self.max_tweets and not no_tweets_limit:
                    break

                if added_tweets == 0:
                    try:
                        while retry_cnt < 15:
                            self.driver.find_element("xpath", "//span[text()='Retry']/../../..").click()
                            self.progress.print_progress(len(self.data), True, retry_cnt, no_tweets_limit)
                            sleep(58)
                            retry_cnt += 1
                            sleep(2)
                    except NoSuchElementException:
                        retry_cnt = 0
                        self.progress.print_progress(len(self.data), False, 0, no_tweets_limit)

                    if empty_count >= 5:
                        if refresh_count >= 3:
                            logger.info("No more tweets to scrape")
                            break
                        refresh_count += 1
                    empty_count += 1
                    sleep(1)
                else:
                    empty_count = refresh_count = 0
            except StaleElementReferenceException:
                sleep(2)
                continue
            except KeyboardInterrupt:
                logger.info("\nKeyboard Interrupt")
                self.interrupted = True
                break
            except Exception as e:
                logger.info(f"\nError scraping tweets: {e}")
                break

        logger.info("Scraping Complete" if len(self.data) >= self.max_tweets or no_tweets_limit else "Scraping Incomplete")
        if not no_tweets_limit:
            logger.info(f"Tweets: {len(self.data)} out of {self.max_tweets}\n")

    def export_data(self):
        logger.info("Saving Tweets to CSV...")
        now = datetime.now()
        folder_path = "../data/tweets/"
        os.makedirs(folder_path, exist_ok=True)
        logger.info(f"Created Folder: {folder_path}")

        data = {
            "Name": [tweet[0] for tweet in self.data],
            "Handle": [tweet[1] for tweet in self.data],
            "Timestamp": [tweet[2] for tweet in self.data],
            "Verified": [tweet[3] for tweet in self.data],
            "Content": [tweet[4] for tweet in self.data],
            "Comments": [tweet[5] for tweet in self.data],
            "Retweets": [tweet[6] for tweet in self.data],
            "Likes": [tweet[7] for tweet in self.data],
            "Analytics": [tweet[8] for tweet in self.data],
            "Tags": [tweet[9] for tweet in self.data],
            "Mentions": [tweet[10] for tweet in self.data],
            "Emojis": [tweet[11] for tweet in self.data],
            "Profile Image": [tweet[12] for tweet in self.data],
            "Tweet Link": [tweet[13] for tweet in self.data],
            "Tweet ID": [f"tweet_id:{tweet[14]}" for tweet in self.data],
        }

        if self.scraper_details["poster_details"]:
            data["Tweeter ID"] = [f"user_id:{tweet[15]}" for tweet in self.data]
            data["Following"] = [tweet[16] for tweet in self.data]
            data["Followers"] = [tweet[17] for tweet in self.data]

        df = pd.DataFrame(data)
        file_path = f"{folder_path}{now.strftime('%Y-%m-%d_%H-%M-%S')}_tweets_1-{len(self.data)}.csv"
        df.to_csv(file_path, index=False, encoding="utf-8")
        logger.info(f"CSV Saved: {file_path}")

    def _input_username(self):
        for _ in range(3):
            try:
                username = self.driver.find_element("xpath", "//input[@autocomplete='username']")
                username.send_keys(self.username)
                username.send_keys(Keys.RETURN)
                sleep(3)
                return
            except NoSuchElementException:
                logger.info("Re-attempting to input username...")
                sleep(2)
        logger.info("There was an error inputting the username")
        self.driver.quit()
        sys.exit(1)

    def _input_unusual_activity(self):
        for _ in range(3):
            try:
                unusual_activity = self.driver.find_element("xpath", "//input[@data-testid='ocfEnterTextTextInput']")
                unusual_activity.send_keys(self.username)
                unusual_activity.send_keys(Keys.RETURN)
                sleep(3)
                return
            except NoSuchElementException:
                sleep(2)

    def _input_password(self):
        for _ in range(3):
            try:
                password = self.driver.find_element("xpath", "//input[@autocomplete='current-password']")
                password.send_keys(self.password)
                password.send_keys(Keys.RETURN)
                sleep(3)
                return
            except NoSuchElementException:
                logger.info("Re-attempting to input password...")
                sleep(2)
        logger.info("There was an error inputting the password.")
        self.driver.quit()
        sys.exit(1)

    def _config_scraper(self, max_tweets=50, scrape_username=None, scrape_hashtag=None, scrape_query=None, scrape_latest=True, scrape_top=False, scrape_poster_details=False):
        self.tweet_ids = set()
        self.data = []
        self.tweet_cards = []
        self.max_tweets = max_tweets
        self.progress = Progress(0, max_tweets)
        self.scraper_details = {
            "type": "Username" if scrape_username else "Hashtag" if scrape_hashtag else "Query" if scrape_query else "Home",
            "username": scrape_username,
            "hashtag": str(scrape_hashtag).replace("#", "") if scrape_hashtag else None,
            "query": scrape_query,
            "tab": "Latest" if scrape_latest else "Top" if scrape_top else "Latest",
            "poster_details": scrape_poster_details,
        }
        self.router = {
            "Username": self.go_to_profile,
            "Hashtag": self.go_to_hashtag,
            "Query": self.go_to_search,
            "Home": self.go_to_home,
        }[self.scraper_details["type"]]

    def go_to_home(self):
        self.driver.get("https://twitter.com/home")
        sleep(3)

    def go_to_profile(self):
        if not self.scraper_details["username"]:
            logger.info("Username is not set.")
            sys.exit(1)
        self.driver.get(f"https://twitter.com/{self.scraper_details['username']}")
        sleep(3)

    def go_to_hashtag(self):
        if not self.scraper_details["hashtag"]:
            logger.info("Hashtag is not set.")
            sys.exit(1)
        url = f"https://twitter.com/hashtag/{self.scraper_details['hashtag']}?src=hashtag_click"
        if self.scraper_details["tab"] == "Latest":
            url += "&f=live"
        self.driver.get(url)
        sleep(3)

    def go_to_search(self):
        if not self.scraper_details["query"]:
            logger.info("Query is not set.")
            sys.exit(1)
        url = f"https://twitter.com/search?q={self.scraper_details['query']}&src=typed_query"
        if self.scraper_details["tab"] == "Latest":
            url += "&f=live"
        self.driver.get(url)
        sleep(3)

    def get_tweet_cards(self):
        self.tweet_cards = self.driver.find_elements("xpath", '//article[@data-testid="tweet" and not(@disabled)]')