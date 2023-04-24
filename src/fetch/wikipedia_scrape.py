import wikipedia
import json
import warnings

'''
The wikipedia API seems to use bs4 library in the background and a warning about the default parser
pops up for redirect pages. Catching the warning here since bs4 used in background so we cannot set default parser.
'''
warnings.filterwarnings("error")


def scrape_wikipedia(query: str) -> str:
    wikipedia.set_lang("en")
    res = wikipedia.search(query)

    for r in res:
        try:
            page = wikipedia.page(title=r, auto_suggest=False)
            summary = wikipedia.summary(title=r, auto_suggest=False).strip()

            '''
            Split by period for now
            Seems like all wikipedia summaries are ended with a space, so split on '. ' to avoid empty string in phrase list
            '''
            phrases = [phrase.strip() for phrase in summary.split('. ')]

            print(format_json(phrases, page.url, query, page.title))

        except:  # Catch exceptions/warnings that pop up for disambiguation/redirect pages
            pass


def format_json(phrases: str, url: str, query: str, page_title: str) -> str:
    source = {
        "site_name": "Wikipedia",
        "url": url,
        "user_search": query,
        "page_title": page_title,
        "language": "English",
    }

    wiki_item = {
        "type": "phrase",
        "phrases": phrases,
        "source": source,
    }

    return json.dumps(wiki_item)


if __name__ == "__main__":
    query = input("Enter a term to search in Wikipedia:")
    scrape_wikipedia(query)
