import re
# import time
from class_helper import Sources, Listing
from selenium.webdriver.common.by import By 
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from selenium_helper import initiate_selenium, find_element


def scrape_listing_pararius(url, see_window, procnum, return_dict):
    driver = initiate_selenium(url, see_window)
    notification = driver.find_elements(By.CLASS_NAME, "page__notifications")
    for n in notification:
        if "The property you want to view is no longer available" in n.get_attribute("textContent"):
            raise Exception("Listing Not Available")

    current_listing = __get_listing_content(url, driver)
    driver.close() 
    return_dict[procnum] = str(current_listing).split('\t')


def __get_listing_content(url, listing):
    # Main Page Details
    title = find_element(listing, By.CSS_SELECTOR, ".listing-detail-summary__title", friendly_name="Title", attribute="textContent")
    print(title)
    title = title.split(": ")[1].split(" in ")
    city, title = title[1], title[0]

    location = find_element(listing, By.CSS_SELECTOR, ".listing-detail-summary__location", friendly_name="location", attribute="textContent")
    zip_regex = re.compile(r"\d{4}\s([A-Z]{2})\s")
    zip_code = zip_regex.search(location).group(0)
    location = location.replace(zip_code, '').strip('(').strip(')')
    zip_code = zip_code.replace(' ', '')

    price = find_element(listing, By.CSS_SELECTOR, ".listing-detail-summary__price", friendly_name="price", attribute="textContent", type_cast="int", remove_strs=["\n", 'per month', ',', '€'])
    offered_since = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--offered_since > .listing-features__main-description", friendly_name="Offered Since", attribute="textContent", remove_strs=['+'])
    if 'week' in offered_since:
        offered_since = date.today() - timedelta(weeks=int(offered_since.replace("week", "").replace("s", "").strip()))
    elif 'month' in offered_since:
        offered_since = date.today() - relativedelta(months=+int(offered_since.replace("month", "").replace("s", "").strip()))
    else:
        offered_since = datetime.strptime(offered_since, '%d-%m-%Y').date()
    acceptance = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--acceptance > .listing-features__main-description", friendly_name="Acceptance", attribute="textContent")
    if 'from' in acceptance.lower():
        acceptance = datetime.strptime(acceptance.replace("From ", ""), '%d-%m-%Y').date()
    contract_duration = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--contract_duration > .listing-features__main-description", friendly_name="Contract Duration", attribute="textContent")

    return Listing(title=title, price=price, city=city, zip_code=zip_code, url=url, offered_since=offered_since,
    acceptance=acceptance, contract_duration=contract_duration, source_found=Sources.Pararius)

# def __get_listing_content(listing):
#     # Main Page Details
#     title = find_element(listing, By.CSS_SELECTOR, ".listing-detail-summary__title", friendly_name="Title", attribute="textContent")
#     print(title)
#     title = title.split(": ")[1].split(" in ")
#     city, title = title[1], title[0]

#     location = find_element(listing, By.CSS_SELECTOR, ".listing-detail-summary__location", friendly_name="location", attribute="textContent")
#     zip_regex = re.compile(r"\d{4}\s([A-Z]{2})\s")
#     zip_code = zip_regex.search(location).group(0)
#     location = location.replace(zip_code, '').strip('(').strip(')')
#     zip_code = zip_code.replace(' ', '')

#     price = find_element(listing, By.CSS_SELECTOR, ".listing-detail-summary__price", friendly_name="price", attribute="textContent", type_cast="int", remove_strs=["\n", 'per month', ',', '€'])
#     surface_area = find_element(listing, By.CSS_SELECTOR, ".illustrated-features__item--surface-area", friendly_name='Surface Area', attribute="textContent", remove_strs=[' m²'])
#     number_of_rooms = find_element(listing, By.CSS_SELECTOR, ".illustrated-features__item--number-of-rooms", friendly_name="Number of Rooms", attribute="textContent", type_cast="int", remove_strs=['room', 's'])
#     for_rent_price = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--for_rent_price > .listing-features__main-description", friendly_name="For Rent Price", attribute="textContent", type_cast="int", remove_strs=[' per month', ',', '€'])
#     description = find_element(listing, By.CLASS_NAME, "listing-detail-description__additional", friendly_name="Description", attribute="text", remove_strs=['Description\n', ('\n',' - '), ('\t',' ')])
#     offered_since = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--offered_since > .listing-features__main-description", friendly_name="Offered Since", attribute="textContent", remove_strs=['+'])
#     if 'week' in offered_since:
#         offered_since = date.today() - timedelta(weeks=int(offered_since.replace("week", "").replace("s", "").strip()))
#     elif 'month' in offered_since:
#         offered_since = date.today() - relativedelta(months=+int(offered_since.replace("month", "").replace("s", "").strip()))
#     else:
#         offered_since = datetime.strptime(offered_since, '%d-%m-%Y').date()
    
#     status = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--status > .listing-features__main-description", friendly_name="Status", attribute="textContent")
#     acceptance = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--acceptance > .listing-features__main-description", friendly_name="Acceptance", attribute="textContent")
#     if 'from' in acceptance.lower():
#         acceptance = datetime.strptime(acceptance.replace("From ", ""), '%d-%m-%Y').date()
#     interior = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--interior > .listing-features__main-description", friendly_name="Interior", attribute="textContent")
#     dwelling_type = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--dwelling_type > .listing-features__main-description", friendly_name="Dwelling Type", attribute="textContent")
#     # interior = listing.find_element(By.CSS_SELECTOR, ".illustrated-features__item--interior").get_attribute("textContent")
#     # surface_area = listing.find_element(By.CSS_SELECTOR, ".listing-features__description--surface_area > .listing-features__main-description").get_attribute("textContent")
#     # number_of_rooms = listing.find_element(By.CSS_SELECTOR, ".listing-features__description--number_of_rooms > .listing-features__main-description").get_attribute("textContent")
    
#     service_costs, plot_size, volume, property_types, construction_type, construction_period = [None] * 6
#     number_of_bedrooms, number_of_bathrooms, number_of_floors, balcony, garden, energy_level = [None] * 6
#     parking, listing_type, garage, insulations, storage, smoking_allowed, pets_allowed = [None] * 7
#     upkeep, situations, sub_description, contract_duration, deposit = [None] * 5

#     upkeep = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--upkeep > .listing-features__main-description", friendly_name="Upkeep", attribute="textContent")
#     situations = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--situations > .listing-features__main-description", friendly_name="Situations", attribute="textContent", remove_strs=[('\n',' - '), '\t'])
#     sub_description = find_element(listing, By.CSS_SELECTOR, ".listing-features__sub-description > li", friendly_name="Sub Description", attribute="textContent")
#     contract_duration = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--contract_duration > .listing-features__main-description", friendly_name="Contract Duration", attribute="textContent")
#     deposit = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--deposit > .listing-features__main-description", friendly_name="Deposit", type_cast="int", attribute="textContent", remove_strs=[',', '€'])

#     service_costs = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--service_costs > .listing-features__main-description", friendly_name="Service Cost", type_cast="int", attribute="textContent", remove_strs=['€'])
#     plot_size = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--plot_size > .listing-features__main-description", friendly_name="Plot Size", attribute="textContent")
#     volume = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--volume > .listing-features__main-description", friendly_name="Volume", attribute="textContent")
#     property_types = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--property_types > .listing-features__main-description", friendly_name="Property Types", attribute="textContent")
#     construction_type = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--construction_type > .listing-features__main-description", friendly_name="Construction Type", attribute="textContent")
#     construction_period = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--construction_period > .listing-features__main-description", friendly_name="Construction Period", type_cast="int", attribute="textContent")
#     number_of_bedrooms = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--number_of_bedrooms > .listing-features__main-description", friendly_name="Number of Bedrooms", type_cast="int", attribute="textContent")
#     number_of_bathrooms = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--number_of_bathrooms > .listing-features__main-description", friendly_name="Number of Bathrooms", type_cast="int", attribute="textContent")
#     number_of_floors = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--number_of_floors > .listing-features__main-description", friendly_name="Number of Floors", type_cast="int", attribute="textContent")
#     facilities = find_element(listing, By.CSS_SELECTOR, '[class^="listing-features__description listing-features__description--facilities"]', friendly_name="Facilities", attribute="textContent", remove_strs=[' ', ('\n', '; '), '\t'], strip_char='; ')
#     balcony = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--balcony > .listing-features__main-description", friendly_name="Balcony", type_cast="bool", attribute="textContent")
#     garden = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--garden > .listing-features__main-description", friendly_name="Garden",type_cast="bool", attribute="textContent")
#     storage = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--storage > .listing-features__main-description", friendly_name="Storage", type_cast="bool", attribute="textContent")
#     parking = find_element(listing, By.CSS_SELECTOR, ".page__details--parking .listing-features__description--available > .listing-features__main-description", friendly_name="Parking", type_cast="bool", attribute="textContent")
#     listing_type = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--type > .listing-features__main-description", friendly_name="Listing Type", attribute="textContent")
#     garage = find_element(listing, By.CSS_SELECTOR, ".page__details--garage .listing-features__main-description", friendly_name="Garage", type_cast="bool", attribute="textContent")
#     insulations = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--insulations > .listing-features__main-description", friendly_name="Insulations", attribute="textContent")
#     energy_level = find_element(listing, By.CSS_SELECTOR, '[class^="listing-features__description listing-features__description--energy-label-"]', friendly_name="Energy Level", attribute="textContent", remove_strs=['\n'])
#     # available = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--available > .listing-features__main-description", friendly_name="Available", type_cast="bool", attribute="textContent")
#     smoking_allowed = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--smoking_allowed > .listing-features__main-description", friendly_name="Smoking Allowed", type_cast="bool", attribute="textContent")
#     pets_allowed = find_element(listing, By.CSS_SELECTOR, ".listing-features__description--pets_allowed > .listing-features__main-description", friendly_name="Pets Allowed", type_cast="bool", attribute="textContent")
    
#     broker = find_element(listing, By.CSS_SELECTOR, ".agent-summary__title-link", friendly_name="broker", attribute="text")
#     broker_link = find_element(listing, By.CSS_SELECTOR, ".agent-summary__title-link", friendly_name="broker", attribute="href")
#     photo_id = None

#     listing = Listing(
#         title=title, city=city, location=location, zip_code=zip_code, price=price, description=description, url=listing.current_url,
#         number_of_rooms=number_of_rooms, for_rent_price=for_rent_price, sub_description=sub_description, 
#         offered_since=offered_since, status=status, acceptance=acceptance, contract_duration=contract_duration, 
#         deposit=deposit, interior=interior, upkeep=upkeep, surface_area=surface_area, dwelling_type=dwelling_type, 
#         situations=situations, service_costs=service_costs, plot_size=plot_size, volume=volume, 
#         property_types=property_types, construction_type=construction_type, construction_period=construction_period, 
#         number_of_bedrooms=number_of_bedrooms, number_of_bathrooms=number_of_bathrooms, number_of_floors=number_of_floors, 
#         balcony=balcony, garden=garden, energy_level=energy_level, parking=parking, listing_type=listing_type, 
#         garage=garage, insulations=insulations, storage=storage, smoking_allowed=smoking_allowed, 
#         pets_allowed=pets_allowed, broker_link=broker_link, broker=broker, source_found=Sources.Pararius, photo_id=photo_id)

#     return listing

