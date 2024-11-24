import asyncio
import ollama
from time import sleep

import toml
from telegram.ext import Application

import webdrivers.firefox
from scrapers.binance.announcement_content import AnnouncementContent
from scrapers.binance.listing_announcements import BinanceListingAnnouncementsScraper
from utils.logger import logger

config = toml.load("../config.toml")
CHAT_ID = config.get("telegram").get("chat_id")
TOKEN = config.get("telegram").get("token")

async def telegram_notice(driver, link):
    application = Application.builder().token(TOKEN).build()
    scraper = AnnouncementContent(driver)
    scraper.scrape(link)
    response = ollama.chat(model='gemma2', messages=[
        {
            'role': 'user',
            'content': 'Find the token address in the following text (extracted from html content)'
                       ', using markdown format in your response, adding some emojis: '
                       '' + scraper.content.text,
        },
    ])
    summary = response['message']['content']
    bot_msg = (f"**[Listing Announcement]** {scraper.title}\n\n"
               f"**[Announcement Time]** {scraper.time}\n\n"
               f"**[LLM Summary]** {summary}\n")
    # print(bot_msg)
    await application.bot.send_message(CHAT_ID, text=bot_msg, parse_mode="Markdown")


def is_valid_listing(link):
    if "binance-will-list" not in link:
        return False
    return True


async def binance_latest_listing(driver):
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
            await telegram_notice(driver, latest_link)


async def binance_latest_20_announcements(driver):
    scraper = BinanceListingAnnouncementsScraper(driver)
    scraper.scrape()
    for link in reversed(scraper.announcement_list):
        if not is_valid_listing(link):
            continue
        await telegram_notice(driver, link)


if __name__ == "__main__":
    _driver = webdrivers.firefox.get_firefox()
    _driver.maximize_window()
    asyncio.run(binance_latest_20_announcements(_driver))
    # binance_latest_listing(_driver)
