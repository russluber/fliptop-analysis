# emcee_scraper.py

import requests
from bs4 import BeautifulSoup

def scrape_names(base_url="https://www.fliptop.com.ph/emcees", max_pages=10):
    """
    Scrapes emcee names from FlipTop website across paginated pages.

    Parameters:
        base_url (str): Base URL for emcee listings.
        max_pages (int): Number of pages to scrape.

    Returns:
        list[str]: List of emcee names scraped from the website.
    """
    emcee_names = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        h4_tags = soup.find_all("h4", class_="text-uppercase")
        if not h4_tags:
            print(f"No emcees found on page {page}. Stopping early.")
            break

        for tag in h4_tags:
            emcee_names.append(tag.get_text(strip=True))

        print(f"Scraped {len(h4_tags)} names from page {page}.")

    return emcee_names


