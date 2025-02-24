import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pyautogui
from loguru import logger

from libchrome import Chrome

CUR_DIR = Path(__file__).parent
PAGES_DIR = CUR_DIR / "pages"
OUTPUT_DIR = CUR_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CAPTCHA_START_IMG_PATH = CUR_DIR / "captcha_start.png"
CAPTCHA_END_IMG_PATH = CUR_DIR / "captcha_end.png"


def load_links() -> Dict[str, List[str]]:
    link_list: Dict[str, List[str]] = {}

    fnames = os.listdir(PAGES_DIR)
    for fname in fnames:
        fpath = PAGES_DIR / fname
        if not fpath.is_file():
            continue

        cat_name = os.path.splitext(fname)[0]
        link_list[cat_name] = []

        with fpath.open("r") as file:
            for line in file:
                gig = json.loads(line)
                link_list[cat_name].append("https://www.fiverr.com" + gig["gig_url"])

    return link_list


def check_captcha(chrome: Chrome, wait_elem_selector: str) -> bool:
    wait_elem = chrome.select_one(wait_elem_selector)
    if wait_elem is not None:
        return True

    captcha_title = chrome.select_one("h1[data-identifier=title]")
    if captcha_title is None:
        return True

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
        start = datetime.now().timestamp()
        img_box = None
        while img_box is None:
            try:
                if datetime.now().timestamp() - start > 20:
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

        return True

    return False


def main():
    link_list = load_links()

    user_data_dir = CUR_DIR / "temp" / f"profile_{time.time()}"
    chrome = Chrome(
        width=800,
        height=600,
        block_image=True,
        user_data_dir=str(user_data_dir),
    )
    chrome.start()

    for cat_name in link_list:
        links = link_list[cat_name]
        cat_dpath = OUTPUT_DIR / cat_name
        cat_dpath.mkdir(parents=True, exist_ok=True)

        for profile_index, profile_link in enumerate(links):
            logger.info(f"cat: {cat_name}, profile: {profile_index}/{len(links)}")

            profile_fpath = cat_dpath / f"{profile_index}.json"
            already_done = False
            if profile_fpath.is_file():
                with profile_fpath.open("r") as file:
                    json_data = json.load(file)
                    if "cat" in json_data and "profile":
                        already_done = True

            if already_done:
                logger.info("already done")
                continue

            while True:
                try:
                    chrome.goto(profile_link, wait_elem_selector="form.search-form")
                    if check_captcha(
                        chrome=chrome,
                        wait_elem_selector="form.search-form",
                    ):
                        body_html = chrome.body()

                        with profile_fpath.open("w") as file:
                            json.dump(
                                {
                                    "cat": cat_name,
                                    "profile": profile_index,
                                    "html": body_html,
                                },
                                file,
                            )
                        break
                except Exception as ex:
                    logger.exception(ex)

                chrome.quit()

                user_data_dir = CUR_DIR / "temp" / f"profile_{time.time()}"
                chrome = Chrome(
                    width=800,
                    height=600,
                    block_image=True,
                    user_data_dir=str(user_data_dir),
                )
                chrome.start()

    chrome.quit()


if __name__ == "__main__":
    main()
