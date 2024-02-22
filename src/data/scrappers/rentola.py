import re
import logging
import pandas as pd
from class_helper import Sources, Listing
from request_helper import initiate_request, find_element
from datetime import date, datetime, timedelta

def_empty_value = ''

__var_dets={
    'header':{
        'id':{
            'html':'div',
            'identifier':'upper-content',
        },
        'properties':{
            'title':{
                'html':'h1',
                'type':'str',
                'identifier':'',
            },
            'location':{
                'html':'p',
                'type':'str',
                'identifier':'location',
                # 'removable':[],
                # 'splitting':[],
            }
        }
    },
    'description':{
        'id':{
            'html':'div',
            'identifier':'description',
        },
        'properties':{
            'description':{
                'html':'p',
                'type':'str',
                'identifier':'',
            }
        }
    },
    'details': {
        'id':{
            'html':'div',
            'identifier':'about',
            'multiple': {'html':'div','type':'str','identifier':'circle'},
            'splitter': ':\n',
        },
    }
}


def generate_rentola_url(base_url: str, location: str, max_price: int):
    return f"{base_url}for-rent?location={location.lower()}&rent=0-{max_price}"


def __get_variable(vars, id: str, type_cast: str='str', removable: list=None):
    if id not in list(vars.keys()):
        print(f' - {id.title()} not found')
        return ''
    val = vars[id]
    removable = [] if removable is None else removable
    for r in removable:
        val = val.replace(r, '')
    val = val.strip().title()
    if type_cast == 'int':
        val = int(val)
    elif type_cast == 'date':
        val = datetime.strptime(val, '%Y-%m-%d').date()
    return val


def __get_listing_content(url, page):
    # Map items into variables
    all_values = {}
    for h in __var_dets.keys():
        section = __var_dets[h]["id"]
        multiple_with_same_class = section["multiple"] if "multiple" in list(section.keys()) else None
        splitter = section['splitter'] if 'splitter' in list(section.keys()) else None
        section = find_element(page, section["html"], class_name=section["identifier"], friendly_name=h)
        if multiple_with_same_class is not None:
            values = section.find_all(multiple_with_same_class["html"], {'class': multiple_with_same_class["identifier"]})
            for v in values:
                c = v.text.strip('\n').lower().split(splitter)
                all_values[c[0]] = c[1]
        else:
            for p in __var_dets[h]["properties"]:        
                value = __var_dets[h]["properties"][p]
                value = find_element(section, value["html"], class_name=value["identifier"], friendly_name=p.title(), type_cast=value["type"], attribute="text")
                all_values[p] = value

    title = __get_variable(vars=all_values, id='title')
    location = __get_variable(vars=all_values, id='location')
    zip_regex = re.compile(r"\d{4}\s([A-Z]{2})\s").search(location)
    zip_code = zip_regex.group(0).replace(' ', '') if zip_regex else ''

    city = __get_variable(vars=all_values, id='city')
    price = __get_variable(vars=all_values, id='price', type_cast='int', removable=['€'])
    acceptance = __get_variable(vars=all_values, id='available from', type_cast='date')
    
    offered_since, contract_duration = [''] * 2

    return Listing(title=title, price=price, city=city, zip_code=zip_code, url=url, offered_since=offered_since,
    acceptance=acceptance, contract_duration=contract_duration, source_found=Sources.Rentola)


# def __get_listing_content(url, page):
#     # Map items into variables
#     all_values = {}
#     for h in __var_dets.keys():
#         section = __var_dets[h]["id"]
#         multiple_with_same_class = section["multiple"] if "multiple" in list(section.keys()) else None
#         splitter = section['splitter'] if 'splitter' in list(section.keys()) else None
#         section = find_element(page, section["html"], class_name=section["identifier"], friendly_name=h)
#         if multiple_with_same_class is not None:
#             values = section.find_all(multiple_with_same_class["html"], {'class': multiple_with_same_class["identifier"]})
#             for v in values:
#                 c = v.text.strip('\n').lower().split(splitter)
#                 all_values[c[0]] = c[1]
#         else:
#             for p in __var_dets[h]["properties"]:        
#                 value = __var_dets[h]["properties"][p]
#                 value = find_element(section, value["html"], class_name=value["identifier"], friendly_name=p.title(), type_cast=value["type"], attribute="text")
#                 all_values[p] = value

#     title = __get_variable(vars=all_values, id='title')
#     location = __get_variable(vars=all_values, id='location')
#     zip_regex = re.compile(r"\d{4}\s([A-Z]{2})\s").search(location)
#     zip_code = zip_regex.group(0).replace(' ', '') if zip_regex else ''
#     # zip_code = location[1].split(' ')
#     # zip_code = ''.join(zip_code)

#     url = url
#     status = 'For rent'
#     city = __get_variable(vars=all_values, id='city')
#     description = __get_variable(vars=all_values, id='description')
#     property_types = __get_variable(vars=all_values, id='property type')
#     number_of_bedrooms = __get_variable(vars=all_values, id='bedrooms', type_cast='int')
#     number_of_bathrooms = __get_variable(vars=all_values, id='bathrooms', type_cast='int')
#     surface_area = __get_variable(vars=all_values, id='area', type_cast='int', removable=['m2'])
#     price = __get_variable(vars=all_values, id='price', type_cast='int', removable=['€'])
#     deposit = __get_variable(vars=all_values, id='deposit', type_cast='int', removable=['€'])
#     acceptance = __get_variable(vars=all_values, id='available from', type_cast='date')
#     pets_allowed = __get_variable(vars=all_values, id='pets allowed')
#     garage = __get_variable(vars=all_values, id='garage')
#     balcony = __get_variable(vars=all_values, id='balcony')
#     garden = __get_variable(vars=all_values, id='garden')
#     parking = __get_variable(vars=all_values, id='parking')
#     interior = __get_variable(vars=all_values, id='furnished')
#     if interior == 'Yes':
#         interior = 'Furnished'
#     elif interior == 'No':
#         interior = 'Upholstered'

#     location, number_of_rooms, for_rent_price, sub_description, offered_since, contract_duration, upkeep, dwelling_type, situations, service_costs, plot_size, volume, construction_type, construction_period, number_of_floors, energy_level, listing_type, insulations, storage, smoking_allowed, broker_link, broker, photo_id = [''] * 23

#     used_properties = ['title', 'location', 'city', 'description', 'property type', 'bedrooms', 'bathrooms', 'area', 'price', 'deposit', 'available from', 'pets allowed', 'garage', 'balcony', 'garden', 'parking', 'furnished']
#     ignored_properties = ['price per m²', 'washing machine', 'terrace']
#     print(f"Additional Properties have been found: {', '.join(list(set(set(all_values.keys()) - set(used_properties) - set(ignored_properties))))}")
#     listing = Listing(
#         title=title, city=city, location=location, zip_code=zip_code, price=price, description=description, url=url,
#         number_of_rooms=number_of_rooms, for_rent_price=for_rent_price, sub_description=sub_description, 
#         offered_since=offered_since, status=status, acceptance=acceptance, contract_duration=contract_duration, 
#         deposit=deposit, interior=interior, upkeep=upkeep, surface_area=surface_area, dwelling_type=dwelling_type, 
#         situations=situations, service_costs=service_costs, plot_size=plot_size, volume=volume, 
#         property_types=property_types, construction_type=construction_type, construction_period=construction_period, 
#         number_of_bedrooms=number_of_bedrooms, number_of_bathrooms=number_of_bathrooms, number_of_floors=number_of_floors, 
#         balcony=balcony, garden=garden, energy_level=energy_level, parking=parking, listing_type=listing_type, 
#         garage=garage, insulations=insulations, storage=storage, smoking_allowed=smoking_allowed, 
#         pets_allowed=pets_allowed, broker_link=broker_link, broker=broker, source_found=Sources.Rentola, photo_id=photo_id)
#     return listing


def scrape_listing_rentola(url, see_window, procnum, return_dict):
    page = initiate_request(url)
    print(f'#### Start: {procnum}: {url}')
    current_listing = __get_listing_content(url, page)
    print(f'#### Complete: {procnum}: {url}')
    return_dict[procnum] = str(current_listing).split('\t')

