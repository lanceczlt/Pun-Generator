import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
 
def get_links(response):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is not None and re.match(r"^https://pun\.me/puns/\w+/$", href):
            if re.match("^https?://", href):
                links.append(href)
            elif href.startswith("/"):
                links.append(url + href)
    return links


def scrape_site(url, visited=set()):
    if url in visited:
        return
    print("Scraping:", url)
    response = requests.get(url, headers=headers)
    html = response.content

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    puns_list = soup.select('.edit.puns, .puns')

    for puns in puns_list:
        puns_items = puns.find_all('li')
        for i, pun in enumerate(puns_items):
            print(f'Pun {i+1}: {pun.text.strip()}')

    visited.add(url)
    links = get_links(response)

    for link in links:
        scrape_site(link, visited)

# URL to scrape
url = 'https://pun.me/puns/'
scrape_site(url)


