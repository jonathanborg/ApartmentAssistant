import time
import logging
import pandas as pd
import multiprocessing
from .funda import generate_funda_url, scrape_listing_funda
from .rentola import generate_rentola_url, scrape_listing_rentola
from .pararius import scrape_listing_pararius
from class_helper import Sources, Listing, has_gemeente
from selenium_helper import initiate_selenium
from request_helper import initiate_request
from selenium.webdriver.common.by import By 

HOME_PAGE_PARARIUS = "https://www.pararius.com"
HOME_PAGE_FUNDA = "https://www.funda.nl/en"
HOME_PAGE_RENTOLA = "https://rentola.nl/en/"


def get_website_data(source: Sources, locations: dict, max_price: int, max_pages: int=None, max_radius: int=None, old_listings_urls: list=None, new_listings_urls: list=None, use_selenium: bool=True, see_window: bool=False, get_new_data: bool=True) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    try:
        target_func = None
        listing_urls = [x for x in new_listings_urls if source.name.lower() in x]
        for location in list(locations.keys()):
            loc_listing_urls, target_func = __get_website_listings(source=source, location=location, max_price=max_price, max_pages=max_pages, max_radius=locations[location], use_selenium=use_selenium, see_window=see_window, get_new_data=get_new_data)
            listing_urls += loc_listing_urls
            
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


def __get_website_listings(source: Sources, location: str, max_price: int, max_pages: int, max_radius: int, use_selenium:bool, see_window:bool, get_new_data: bool):
    logger = logging.getLogger(__name__)
    
    #To Remove - Start
    # url = "https://rentola.nl/en/listings/te-huur-appartement-hoge-nieuwstraat-in-dordrecht-db5f9d"
    # procnum = 0
    # return_dict = {}
    # scrape_listing_rentola(url, see_window, procnum, return_dict)
    #To Remove - End
    all_listings = []
    website_url, page_ext, listings_selector, pagination_link_selector, target_func = __get_main_website_details(source=source, location=location, max_price=max_price, max_pages=max_pages, max_radius=max_radius, use_selenium=use_selenium, see_window=see_window)
    if get_new_data:
        i = 1
        total_pages = __get_total_pages(None, source, use_selenium, website_url, see_window, pagination_link_selector)
        logger.info(f'---- Total Pages: {total_pages}; Main Page: {website_url};')
        total_pages = 1 if total_pages is None else total_pages
        while i < total_pages+1:
            logger.info(f'---- {source.name} Page {i}')
            url = f'{website_url}{page_ext}{i}' if i > 1 else website_url
            logger.info(f'---- Getting all listings on page')
            current_listings, page = __get_page_listings(source=source, url=url, listings_selector=listings_selector, use_selenium=use_selenium, see_window=see_window)
            all_listings += current_listings
            if source.Rentola:
                more_pages = __get_total_pages(page=page, source=source, use_selenium=use_selenium, website_url=url, see_window=see_window, pagination_link_selector=pagination_link_selector)
                if more_pages is None:
                    total_pages += 1
            i += 1
    # for i in range(1, total_pages+1):
    #     logger.info(f'---- {source.name} Page {i}')
    #     url = f'{website_url}{page_ext}{i}' if i > 1 else website_url
    #     logger.info(f'---- Getting all listings on page')
    #     all_listings += __get_page_listings(url=url, listings_selector=listings_selector, use_selenium=use_selenium, see_window=see_window)    
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
        listings_selector = 'flex justify-between'
        pagination_link_selector = "pagination"
        target_func = scrape_listing_funda
    elif source == Sources.Rentola:
        website_url = generate_rentola_url(base_url=HOME_PAGE_RENTOLA, location=location, max_price=max_price)
        page_ext = "&page="
        listings_selector = 'property'
        pagination_link_selector = "pagination-load-more"
        target_func = scrape_listing_rentola
    else:
        raise NotImplementedError()

    return website_url, page_ext, listings_selector, pagination_link_selector, target_func


def __get_total_pages(page, source: Sources, use_selenium: bool, website_url: str, see_window: bool, pagination_link_selector: str ):
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
        if page is None:
            page = initiate_request(website_url)
        if source == Sources.Funda:
            pagation_result = page.find('ul', {'class': pagination_link_selector})
            total_pages = [int(x.text) for x in page.find('ul', {'class': pagination_link_selector}).contents if x.text.isdigit()]
        elif source == Sources.Rentola:
            pagation_result = page.find('div', {'id': pagination_link_selector})
            total_pages = 1 if pagation_result is None or 'load more' not in pagation_result.text.lower() else None
            return total_pages
        else: 
            raise NotImplementedError()
    return max(total_pages) if total_pages is not None and len(total_pages) > 0 else 1


def __get_page_listings(source: Sources, url: str, listings_selector: str, use_selenium: bool, see_window: bool):
    logger = logging.getLogger(__name__)
    page, all_listings_elements = None, None
    if use_selenium:
        driver = initiate_selenium(url, see_window)
        logger.info(f'---- Getting all listings on page')
        all_listings_elements = [x.get_attribute("href") for x in driver.find_elements(By.CSS_SELECTOR, listings_selector)]
        driver.close()
    else:
        page = initiate_request(url)
        all_listings_elements = page.find_all('div', {'class': listings_selector})
        # TODO - /en/ is for Funda - Double check with out sources
        if source == Sources.Funda:
            all_listings_elements = ['.nl/en/'.join(x.find('a').get('href').split('.nl/')) for x in all_listings_elements]    
        elif source == Sources.Rentola:
            all_listings_elements = [f"{HOME_PAGE_RENTOLA.strip('en/')}{x.find('a').get('href')}" for x in all_listings_elements]    
    return all_listings_elements, page
            

def __get_website_listing_details(listing_urls: list, target_func, see_window) -> list:
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for i, url in enumerate(listing_urls):
        # scrape_listing_rentola(url, see_window, i,  return_dict)
        # print()
        wait_time = 5 if see_window else 1
        time.sleep(wait_time)
        p = multiprocessing.Process(target=target_func, args=(url, see_window, i,  return_dict)) 
        jobs.append(p)
        p.start()

    for p in jobs: 
        p.join()

    return return_dict.values()

