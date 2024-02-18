import time
import logging
import pandas as pd
import multiprocessing
from .funda import generate_funda_url, scrape_listing_funda
from .pararius import scrape_listing_pararius
from class_helper import Sources, Listing, has_gemeente
from selenium_helper import initiate_selenium
from request_helper import initiate_request
from selenium.webdriver.common.by import By 

HOME_PAGE_PARARIUS = "https://www.pararius.com"
HOME_PAGE_FUNDA = "https://www.funda.nl/en"


def get_website_data(source: Sources, location: str, max_price: int, max_pages: int=None, max_radius: int=None, old_listings_urls: list=None, use_selenium: bool=True, see_window: bool=False) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    try:
        listing_urls, target_func = __get_website_listings(source=source, location=location, max_price=max_price, max_pages=max_pages, max_radius=max_radius, use_selenium=use_selenium, see_window=see_window)
    except Exception as ex:
        if str(ex) == "Bot Detected":
            logger.warning(f'---- Error: Bot has been detected; no pages scrapped - run in normal mode')
            return None
        elif str(ex) == "No Listings Found":
            logger.warning(f'---- Notification: No Listings are found in {location}: (0-{max_price}) under {source.name}')
            return None
        raise ex
    if old_listings_urls is not None:
        listing_urls = list(set(listing_urls) - set(old_listings_urls))

    logger.info(f'---- Extracting {len(listing_urls)} New Listings')
    listing_data = __get_website_listing_details(listing_urls=listing_urls, target_func=target_func, see_window=see_window)
    return pd.DataFrame(listing_data, columns=Listing.header().split(', '))


def __get_website_listings(source: Sources, location: str, max_price: int, max_pages: int, max_radius: int, use_selenium:bool, see_window:bool):
    logger = logging.getLogger(__name__)
    
    #To Remove - Start
    # url = "https://www.funda.nl/en/huur/barendrecht/huis-43460478-schapenburg-14/"
    # url = "https://www.funda.nl/en/huur/rotterdam/appartement-42338197-meyenhage-201/"
    # procnum = 0
    # return_dict = {}
    # scrape_listing_funda(url, see_window, procnum, return_dict)
    #To Remove - End

    website_url, page_ext, total_pages, listings_selector, target_func = __get_main_website_details(source=source, location=location, max_price=max_price, max_pages=max_pages, max_radius=max_radius, use_selenium=use_selenium, see_window=see_window)
    logger.info(f'---- Total Pages: {total_pages}; Main Page: {website_url};')
    all_listings = []
    for i in range(1, total_pages+1):
        logger.info(f'---- {source.name} Page {i}')
        url = f'{website_url}{page_ext}{i}' if i > 1 else website_url
        logger.info(f'---- Getting all listings on page')
        all_listings += __get_page_listings(url=url, listings_selector=listings_selector, use_selenium=use_selenium, see_window=see_window)
    
    return list(set(all_listings)), target_func


def __get_main_website_details(source: Sources, location: str, max_price: int, max_pages: int, max_radius: int, use_selenium: bool, see_window: bool):
    if source == Sources.Pararius:
        website_url = f"{HOME_PAGE_PARARIUS}/apartments/{location.lower()}/0-{max_price}"
        page_ext = "/page-"
        listings_selector = '[class$="listing-search-item__link--title"'
        pagination_link_selector = "pagination__link"
        target_func = scrape_listing_pararius
    elif source == Sources.Funda:
        website_url = generate_funda_url(base_url=HOME_PAGE_FUNDA, location=location, max_price=max_price, max_radius=max_radius, append_gemeente=has_gemeente[location])
        page_ext = "&search_result="
        # listings_selector = '[data-test-id="object-image-link"]'
        listings_selector = 'flex justify-between'
        pagination_link_selector = "pagination"
        target_func = scrape_listing_funda
    else:
        raise NotImplementedError()

    if use_selenium:
        driver = initiate_selenium(website_url, see_window)
        bot_message = driver.find_elements(By.ID, "message")
        for b in bot_message:
            if 'something about your browser or behaviour made us think you might be a bot' in b.get_attribute("textContent"):
                raise Exception("Bot Detected")
        notification = driver.find_elements(By.CLASS_NAME, "page__notifications")
        for n in notification:
            if "Unfortunately there are no results for your search" in n.get_attribute("textContent"):
                raise Exception("No Listings Found")
        all_pages = driver.find_elements(By.CLASS_NAME, pagination_link_selector)
        total_pages = [int(x.get_attribute("textContent")) for x in all_pages if x.text.isdigit()]
        driver.close()
            
    else:
        page = initiate_request(website_url)
        pagation_result = page.find('ul', {'class': pagination_link_selector})
        total_pages = [int(x.text) for x in page.find('ul', {'class': pagination_link_selector}).contents if x.text.isdigit()]
    
    total_pages = max(total_pages) if total_pages is not None and len(total_pages) > 0 else 1
    return website_url, page_ext, total_pages, listings_selector, target_func


def __get_page_listings(url: str, listings_selector: str, use_selenium: bool, see_window: bool):
    logger = logging.getLogger(__name__)
    if use_selenium:
        driver = initiate_selenium(url, see_window)
        logger.info(f'---- Getting all listings on page')
        all_listings_elements = [x.get_attribute("href") for x in driver.find_elements(By.CSS_SELECTOR, listings_selector)]
        driver.close()
        return all_listings_elements
    else:
        page = initiate_request(url)
        all_listings_elements = page.find_all('div', {'class': listings_selector})
        # TODO - /en/ is for Funda - Double check with out sources
        return ['.nl/en/'.join(x.find('a').get('href').split('.nl/')) for x in all_listings_elements]
            

def __get_website_listing_details(listing_urls: list, target_func, see_window) -> list:
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for i, url in enumerate(listing_urls):
        # scrape_listing_funda(url, see_window, i,  return_dict)
        # print()
        wait_time = 5 if see_window else 1
        time.sleep(wait_time)
        p = multiprocessing.Process(target=target_func, args=(url, see_window, i,  return_dict)) 
        jobs.append(p)
        p.start()

    for p in jobs: 
        p.join()

    return return_dict.values()

