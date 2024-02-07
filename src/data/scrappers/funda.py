import logging
import pandas as pd
from class_helper import Sources, Listing
from selenium_helper import initiate_selenium, find_element


def generate_funda_url(base_url: str, location: str, max_price: int, max_radius: int):
    if max_radius is None:
        max_radius = 10
    return f"{base_url}/zoeken/huur?selected_area=%5B%22gemeente-{location.lower()},{max_radius}%22%5D&price=%22-{max_price}%22"


def __get_listing_content(page_content):
    # Map items into variables
    listing = Listing(
        title=title, city=city, location=location, zip_code=zip_code, price=price, description=description, url=listing.current_url,
        number_of_rooms=number_of_rooms, for_rent_price=for_rent_price, sub_description=sub_description, 
        offered_since=offered_since, status=status, acceptance=acceptance, contract_duration=contract_duration, 
        deposit=deposit, interior=interior, upkeep=upkeep, surface_area=surface_area, dwelling_type=dwelling_type, 
        situations=situations, service_costs=service_costs, plot_size=plot_size, volume=volume, 
        property_types=property_types, construction_type=construction_type, construction_period=construction_period, 
        number_of_bedrooms=number_of_bedrooms, number_of_bathrooms=number_of_bathrooms, number_of_floors=number_of_floors, 
        balcony=balcony, garden=garden, energy_level=energy_level, parking=parking, listing_type=listing_type, 
        garage=garage, insulations=insulations, storage=storage, smoking_allowed=smoking_allowed, 
        pets_allowed=pets_allowed, broker_link=broker_link, broker=broker, source_found=Sources.Funda, photo_id=photo_id)
    return listing


def scrape_listing_funda(url, procnum, return_dict):
    session = requests.Session()
    response = session.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"})
    page = BeautifulSoup(response.text, 'html.parser')
    current_listing = __get_listing_content(driver)
    return_dict[procnum] = str(current_listing).split('\t')

