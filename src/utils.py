import wikipedia
import re


def wiki(driver_name: str) -> str:
    """Return the info about driver from wikipedia.
    Original text returns with headings enclosed by '==='. This is replaced by bold text"""
    wiki_text = wikipedia.page(driver_name).content
    wiki_text_with_formatted_headings = re.sub(r'=+\s*(.*?)\s*=+', r'<b>\1</b>', wiki_text)
    return wiki_text_with_formatted_headings
