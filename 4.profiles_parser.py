from loguru import logger
import json
import os
from pathlib import Path
from typing import Any, Dict, List
import csv

from bs4 import BeautifulSoup

CUR_DIR = Path(__file__).parent
PAGES_DIR = CUR_DIR / "pages"
PAGES_DIR.mkdir(parents=True, exist_ok=True)


def main():
    cat_fnames = os.listdir(PAGES_DIR)
    for cat_fname in cat_fnames:
        cat_fpath = PAGES_DIR / cat_fname
        if not cat_fpath.is_file():
            continue

        cat_name = os.path.splitext(cat_fname)[0]
        save_path = CUR_DIR / "output" / (cat_name + ".csv")
        profiles: List[Dict[str, Any]] = []

        with cat_fpath.open("r") as file:
            for lineno, line in enumerate(file):
                logger.info(f"cat: {cat_name}, index: {lineno}")
                profile_fpath = CUR_DIR / "output" / cat_name / f"{lineno}.json"
                with profile_fpath.open("r") as profile_file:
                    profile_data = json.load(profile_file)
                    profile_html = profile_data["html"]
                    soup = BeautifulSoup(profile_html, "html.parser")
                    raw_profile_info: Dict[str, Any] = json.loads(
                        soup.select_one("#perseus-initial-props").text
                    )

                    general = raw_profile_info.get("general", {})
                    profiles.append({
                        "gigId": general.get("gigId"),
                        "gigStatus": general.get("gigStatus"),
                        "categoryId": general.get("categoryId"),
                        "categoryName": general.get("categoryName"),
                        "categorySlug": general.get("categorySlug"),
                        "subCategoryId": general.get("subCategoryId"),
                        "subCategoryName": general.get("subCategoryName"),
                        "subCategorySlug": general.get("subCategorySlug"),
                        "nestedSubCategoryId": general.get("nestedSubCategoryId"),
                        "nestedSubCategorySlug": general.get("nestedSubCategorySlug"),
                        "isOnVacation": general.get("isOnVacation"),
                        "isBuyerBlocked": general.get("isBuyerBlocked"),
                        "isPro": general.get("isPro"),
                        "isHandpicked": general.get("isHandpicked"),
                        "isStudio": general.get("isStudio"),
                        "gigTitle": general.get("gigTitle"),
                        "sellerId": general.get("sellerId"),
                        "traffiqed": general.get("traffiqed"),
                        "isSellerBlocked": general.get("isSellerBlocked"),
                        "gigVisibleToSeller": general.get("gigVisibleToSeller"),
                        "gigVisibleToBuyer": general.get("gigVisibleToBuyer"),
                        "isTrustedUser": general.get("isTrustedUser"),
                        "includeWorkSample": general.get("includeWorkSample"),
                    })

        with open(save_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=profiles[0].keys())
            writer.writeheader()
            writer.writerows(profiles)

        print(f"Data saved to {save_path}")


if __name__ == "__main__":
    main()
