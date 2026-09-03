import json
from pathlib import Path

INPUT_FILE = Path("blogs.json")
OUTPUT_FILE = Path("blogs_updated.json")

OLD_PATH = "/blogs/news/"
NEW_PATH = "/blog/"


def update_content_html(data):
    if isinstance(data, list):
        for item in data:
            update_content_html(item)

    elif isinstance(data, dict):
        if isinstance(data.get("content_html"), str):
            data["content_html"] = data["content_html"].replace(
                OLD_PATH,
                NEW_PATH,
            )

        for value in data.values():
            if isinstance(value, (dict, list)):
                update_content_html(value)


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    update_content_html(data)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Done. Updated JSON saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()