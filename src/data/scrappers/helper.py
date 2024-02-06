import logging
import pandas as pd
import multiprocessing
from .funda import generate_funda_url, scrape_listing_funda
from .pararius import scrape_listing_pararius
from class_helper import Sources, Listing
from selenium_helper import initiate_selenium
from selenium.webdriver.common.by import By 

HOME_PAGE_PARARIUS = "https://www.pararius.com"
HOME_PAGE_FUNDA = "https://www.funda.nl/en"


def get_website_data(source: Sources, location: str, max_price: int, max_pages: int=None, max_radius: int=None, old_listings_urls: list=None) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    listing_urls, target_func = __get_website_listings(source=source, location=location, max_price=max_price, max_pages=max_pages, max_radius=max_radius)
    if old_listings_urls is not None:
        listing_urls = list(set(listing_urls) - set(old_listings_urls))

    logger.info(f'---- Extracting {len(listing_urls)} New Listings')
    listing_data = __get_website_listing_details(listing_urls=listing_urls, target_func=target_func)
    return pd.DataFrame(listing_data, columns=Listing.header().split(', '))


def __get_website_listings(source: Sources, location: str, max_price: int, max_pages: int, max_radius: int):
    logger = logging.getLogger(__name__)
    
    website_url, page_ext, total_pages, listings_selector, driver, target_func = __get_main_website_details(source=source, location=location, max_price=max_price, max_pages=max_pages, max_radius=max_radius)
    all_listings = []
    for i in range(1, total_pages+1):
        logger.info(f'---- {source.name} Page {i}')
        if i > 1:
            url = f'{website_url}{page_ext}{i+1}'
            driver.get(url)

        logger.info(f'---- Getting all listings on page')
        all_listings_elements = driver.find_elements(By.CSS_SELECTOR, listings_selector)
        all_listings += [x.get_attribute("href") for x in all_listings_elements]
    driver.close()
    return list(set(all_listings)), target_func


def __get_main_website_details(source: Sources, location: str, max_price: int, max_pages: int, max_radius: int):
    if source == Sources.Pararius:
        website_url = f"{HOME_PAGE_PARARIUS}/apartments/{location.lower()}/0-{max_price}"
        page_ext = "/page-"
        listings_selector = '[class$="listing-search-item__link--title"'
        pagination_link_selector = "pagination__link"
        target_func = scrape_listing_pararius
    elif source == Sources.Funda:
        website_url = generate_funda_url(base_url=HOME_PAGE_FUNDA, location=location, max_price=max_price, max_radius=max_radius)
        page_ext = "&search_result="
        listings_selector = '[data-test-id="object-image-link"]'
        pagination_link_selector = "pagination"
        target_func = scrape_listing_funda
        
        all_pages = driver.find_elements(By.CLASS_NAME, pagination_link_selector)
        total_pages = max([int(x.get_attribute("textContent")) for x in all_pages if x.text.isdigit()]) if len(all_pages) > 0 else 1

    else:
        raise NotImplementedError()

    driver = initiate_selenium(website_url)
    all_pages = driver.find_elements(By.CLASS_NAME, pagination_link_selector)
    total_pages = max([int(x.get_attribute("textContent")) for x in all_pages if x.text.isdigit()]) if len(all_pages) > 0 else 1
    if max_pages is not None and max_pages < total_pages:
        total_pages = max_pages

    return website_url, page_ext, total_pages, listings_selector, driver, target_func


def __get_website_listing_details(listing_urls: list, target_func) -> list:
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for i, url in enumerate(listing_urls):
        p = multiprocessing.Process(target=target_func, args=(url, i,  return_dict)) 
        jobs.append(p)
        p.start()

    for p in jobs: 
        p.join()

    return return_dict.values()
