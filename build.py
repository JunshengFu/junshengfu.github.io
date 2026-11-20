import argparse
import calendar
import json
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
MARKER = "<!-- NEWS_CONTENT -->"


def news_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", value):
        raise ValueError("News dates must use YYYY, YYYY-MM or YYYY-MM-DD.")
    parts = [int(part) for part in value.split("-")]
    year, month, day = (parts + [1, 1])[:3]
    parsed = date(year, month, day)
    label = str(year)
    if len(parts) >= 2:
        label = f"{calendar.month_abbr[month]} {year}"
    if len(parts) == 3:
        label = f"{calendar.month_abbr[month]} {day}, {year}"
    return parsed, label


def render_news(items):
    if not isinstance(items, list):
        raise ValueError("News must be a JSON array.")
    ordered = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Every news item must be an object.")
        parsed, label = news_date(item.get("date"))
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Every news item needs non-empty text.")
        url = item.get("url")
        link_text = item.get("link_text")
        content = escape(text)
        if link_text is not None and url is None:
            raise ValueError("News link text requires a URL.")
        if url is not None:
            if not isinstance(url, str):
                raise ValueError("News URLs must be strings.")
            target = urlsplit(url)
            if target.scheme not in ("http", "https") or not target.netloc or any(character.isspace() for character in url):
                raise ValueError("News URLs must be complete HTTP or HTTPS links.")
            href = escape(url, quote=True)
            if link_text is None:
                content = f'<a href="{href}">{content}</a>'
            else:
                if not isinstance(link_text, str) or not link_text.strip() or text.count(link_text) != 1:
                    raise ValueError("News link text must appear exactly once in the news text.")
                before, _, after = text.partition(link_text)
                content = f'{escape(before)}<a href="{href}">{escape(link_text)}</a>{escape(after)}'
        row = f'<li><time datetime="{escape(item["date"], quote=True)}">{label}</time><p>{content}</p></li>'
        ordered.append((parsed, row))
    ordered.sort(key=lambda entry: entry[0], reverse=True)
    rows = [entry[1] for entry in ordered]
    if not rows:
        return '<p class="muted">Updates coming soon.</p>'
    output = '<ul class="news-list">\n' + "\n".join(rows[:5]) + "\n</ul>"
    if len(rows) > 5:
        output += '\n<details class="news-archive"><summary><span class="when-closed">All news</span><span class="when-open">Less news</span></summary><ul class="news-list">\n'
        output += "\n".join(rows[5:]) + "\n</ul></details>"
    return output


def build(check=False):
    template = (ROOT / "_templates/index.html").read_text(encoding="utf-8")
    if template.count(MARKER) != 1:
        raise ValueError("The template must contain exactly one News marker.")
    items = json.loads((ROOT / "_data/news.json").read_text(encoding="utf-8"))
    result = template.replace(MARKER, render_news(items))
    destination = ROOT / "index.html"
    if check:
        if not destination.exists() or destination.read_text(encoding="utf-8") != result:
            raise ValueError("index.html is out of date. Run python3 build.py.")
        print("Generated page is up to date.")
    else:
        destination.write_text(result, encoding="utf-8")
        print(f"Built {destination.name} with {len(items)} news items.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the static homepage; no dependencies required.")
    parser.add_argument("--check", action="store_true", help="Check that the generated page is up to date.")
    arguments = parser.parse_args()
    build(check=arguments.check)