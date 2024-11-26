import json
import os
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup

CUR_DIR = Path(__file__).parent
CATEGORY_DIR = CUR_DIR / "categories"
PAGES_DIR = CUR_DIR / "pages"
PAGES_DIR.mkdir(parents=True, exist_ok=True)


def main():
    cat_dnames = os.listdir(CATEGORY_DIR)
    for cat_dname in cat_dnames:
        cat_dpath = CATEGORY_DIR / cat_dname
        if not os.path.isdir(cat_dpath):
            continue

        save_path = PAGES_DIR / (cat_dname + ".jsonl")
        gig_list: List[Dict[str, Any]] = []

        page_fnames = os.listdir(cat_dpath)
        for page_fname in page_fnames:
            page_fpath = cat_dpath / page_fname
            if not os.path.isfile(page_fpath):
                continue

            with page_fpath.open("r") as file:
                page = json.load(file)
                body_html = page["html"]

                soup = BeautifulSoup(body_html, "html.parser")
                script = soup.select_one("#perseus-initial-props")
                json_data = json.loads(script.text)

                for gig in json_data["listings"][0]["gigs"]:
                    gig_list.append(gig)

        with save_path.open("w") as file:
            for gig in gig_list:
                file.write(json.dumps(gig) + "\n")


if __name__ == "__main__":
    main()
