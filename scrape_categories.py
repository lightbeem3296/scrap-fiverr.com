import json
import time
from datetime import datetime
from pathlib import Path

import pyautogui
from bs4 import BeautifulSoup
from loguru import logger

from libchrome import Chrome

CATEGORY_LINKS = [
    "https://www.fiverr.com/categories/programming-tech/ai-coding/custom-gpts",
    "https://www.fiverr.com/categories/programming-tech/ai-coding/ai-agents-development",
    "https://www.fiverr.com/categories/programming-tech/ai-coding/ai-fine-tuning",
    "https://www.fiverr.com/categories/programming-tech/software-development/scripting",
    "https://www.fiverr.com/categories/programming-tech/support-it-services/server-administrations",
    "https://www.fiverr.com/categories/programming-tech/chatbots",
    "https://www.fiverr.com/categories/programming-tech/ai-coding/ai-chatbot",
    "https://www.fiverr.com/categories/programming-tech/ai-coding/ai-applications",
    "https://www.fiverr.com/categories/programming-tech/ai-coding/ai-integrations",
]

CUR_DIR = Path(__file__).parent
CATEGORY_DIR = CUR_DIR / "categories"
CATEGORY_DIR.mkdir(parents=True, exist_ok=True)

CAPTCHA_START_IMG_PATH = CUR_DIR / "captcha_start.png"
CAPTCHA_END_IMG_PATH = CUR_DIR / "captcha_end.png"

USER_DATA_DIR = CUR_DIR / "profile"


def check_captcha(chrome: Chrome, wait_elem_selector: str):
    while True:
        wait_elem = chrome.select_one(wait_elem_selector)
        if wait_elem is not None:
            break

        captcha_title = chrome.select_one("h1[data-identifier=title]")
        if captcha_title is None:
            return

        if captcha_title().strip() == "It needs a human touch":
            logger.info("captcha detected")

            # wait until captcha start button
            logger.info("waiting for captcha button ...")
            img_box = None
            while img_box is None:
                try:
                    img_box = pyautogui.locateOnScreen(
                        str(CAPTCHA_START_IMG_PATH),
                        grayscale=True,
                        confidence=0.9,
                    )
                except Exception as ex:
                    logger.exception(ex)
                time.sleep(0.1)
            logger.info(f"captcha detected at {img_box}")

            pyautogui.moveTo(
                img_box.left + img_box.width // 2,
                img_box.top + img_box.height // 2,
                duration=0.1,
            )
            pyautogui.mouseDown()

            logger.info("waiting for captcha done ...")
            start = datetime.datetime.now().timestamp()
            img_box = None
            while img_box is None:
                try:
                    if datetime.datetime.now().timestamp() - start > 20:
                        logger.error("waiting timeout")
                        break
                    img_box = pyautogui.locateOnScreen(
                        str(CAPTCHA_END_IMG_PATH),
                        grayscale=True,
                        confidence=0.9,
                    )
                except:  # noqa: E722
                    pass
                time.sleep(0.1)
            pyautogui.mouseUp()
            logger.info("captcha done")


def main():
    chrome = Chrome(
        width=800,
        height=600,
        block_image=True,
        user_data_dir=str(USER_DATA_DIR),
    )
    chrome.start()

    for category_index, category_link in enumerate(CATEGORY_LINKS):
        category_dpath = CATEGORY_DIR / f"{category_index}"
        category_dpath.mkdir(parents=True, exist_ok=True)

        logger.info(f"category: {category_index} > {category_link}")

        # goto category page
        chrome.goto(category_link, wait_elem_selector="form.search-form")
        check_captcha(chrome=chrome, wait_elem_selector="form.search-form")

        page_number = 0

        # loop all pages
        while True:
            page_number += 1
            logger.info(f"page: {page_number}")

            page_fpath = category_dpath / f"{page_number}.json"

            body_html = chrome.body()
            soup = BeautifulSoup(body_html, "html.parser")

            with page_fpath.open("w") as file:
                json.dump(
                    {
                        "category": category_index,
                        "page": page_number,
                        "html": body_html,
                    },
                    file,
                    indent=2,
                )

            # goto next page
            next_btn = soup.select_one("a[aria-label=Next]")
            if next_btn is None:
                logger.info("next page btn not found")
                break
            else:
                next_page_link = next_btn.attrs["href"]
                chrome.goto(next_page_link, wait_elem_selector="form.search-form")
                check_captcha(chrome=chrome, wait_elem_selector="form.search-form")

    chrome.quit()


if __name__ == "__main__":
    main()
