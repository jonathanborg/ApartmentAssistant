import re
import logging
import pandas as pd
from class_helper import Sources, Listing
from request_helper import initiate_request, find_element
from datetime import date, datetime, timedelta

def_empty_value = ''

__variable_details={
    'GroupName':{
        'selectors': [],
        'variables': {
        }
    },
    'price':{
        'identifier':[],
        'removable':[],
        'splitting':[],
        'type':''
    }
}

__translations_nl_en={
    'op': 'at',
    'het': 'the',
    'weg': 'road',
    'bad': 'bath', 
    'slaap': 'bed',
    'kamer': 'room',
    'maand': 'month',
    'Ligbad': 'Bath',
    'glas': 'glazing',
    'zuiden': 'south',
    'zolder': 'attic',
    'rustige': 'quiet',
    'achterom': 'rear',
    'Aan': 'Alongside', 
    'douche': 'shower',
    'dubbel': 'Double',
    'Balkon': 'Balcony',
    'aanwezig':'present',
    'Gelegen': 'Located',
    'Achtertuin': 'Garden',
    'woonlagen': 'stories',
    'volledig': 'Completely',
    'beschikbaar': 'For rent',
    'geïsoleerd': 'insulated',
    'appartement': 'apartment',
    'beschikbaar': 'available',
    'bereikbaar': 'accessible',
    'Gemeubileerd': 'Furnished',
    'tussenwoning': 'row house',
    'Gestoffeerd':'Upholstered',
    'onder optie': 'under option',
    'Galerijflat': 'Gallery flat',
    'Nieuwbouw': 'New development',
    'Dakisolatie': 'Roof insulation',
    'Parkeerplaats': 'Parking place',
    'parkeergarage': 'parking garage',
    'muurisolatie': 'wall insulation',
    'Betaald parkeren': 'Paid parking',
    'woonwijk': 'residential district',
    'Bovenwoning': 'Upstairs apartment',
    'vloerisolatie': 'floor insulation',
    'Stadsverwarming': 'District heating',
    'openbaar parkeren': 'public parking',
    'Onbepaalde tijd': 'Unlimited period',
    'Eengezinswoning': 'Single-family home',
    'Tijdelijke verhuur': 'Temporary rental',
    'in overleg': 'available in consultation',
    'verhuurd onder voorbehoud': 'under option',
    'Portiekflat': 'Apartment with shared street entrance',
}

def generate_funda_url(base_url: str, location: str, max_price: int, max_radius: int, append_gemeente: bool):
    if max_radius is None:
        max_radius = 10
    max_radius = f'{max_radius}km'
    return f"{base_url}/zoeken/huur?selected_area=%5B%22gemeente-{location.lower()},{max_radius}%22%5D&price=%22-{max_price}%22&object_type=%5B%22apartment%22,%22house%22%5D"


def __get_price_details(datatbl):
    price, deposit, offered_since, contract_duration, status, acceptance = [def_empty_value] * 6
    for dt in datatbl.find_all('dt', text=False):
        try:
            field_name = dt.text.strip()
            value = dt.findNext("dd").text.strip()
            if field_name in ['Rental price', 'Huurprijs']:
                price = value.replace('€', '').replace(',', '').replace('.', '')
                price = int(price.split('per month')[0].split('per maand')[0].strip())
            elif field_name in ['Deposit', 'Waarborgsom']:
                if value == 'None' or value == '':
                    deposit = ''
                else:
                    deposit = int(value.replace('€', '').replace(',', '').replace('.', '').replace('one-off','').replace('eenmalig', '').strip())
            elif field_name in ['Listed since', 'Aangeboden sinds']:
                offered_since = value
            elif field_name in ['Rental agreement', 'Huurovereenkomst']:
                contract_duration = value.replace('Onbepaalde tijd','Unlimited period').replace('Tijdelijke verhuur', 'Temporary rental').replace('Indefinite duration','Unlimited period')
            elif field_name == 'Status':
                status = value.lower().replace('beschikbaar', 'For rent').replace('onder optie', 'under option').replace('verhuurd onder voorbehoud', 'under option').replace('under option', 'Rented under option').replace('reservation', 'option').replace('available', 'For rent')
            elif field_name in ['Acceptance', 'Aanvaarding']:
                acceptance = value.lower().replace('in overleg', 'available in consultation').replace('beschikbaar', 'available').replace(' per ', ' on ').replace('available on', '').replace('available', '').strip().capitalize()
                acc_s = re.compile(r'(\d+)(-?/?)(\d+)(-?/?)(\d+)').search(value)
                acceptance = datetime.strptime(f'{int(acc_s.group(1))}-{int(acc_s.group(3))}-{int(acc_s.group(5))}', '%m-%d-%Y').date() if acc_s else acceptance
            else:
                print(f' + Additional Field has been found: {field_name}')
        except Exception as ex:
            print(f' -- Exception: {field_name}: {ex}')
            continue

    __check_if_variable_assigned({'Price':price, 'Deposit':deposit, 'Offered Since':offered_since, 'Contract Duration':contract_duration, 'Status':status, 'Acceptance':acceptance}, def_empty_value)
    return price, deposit, offered_since, contract_duration, status, acceptance


def __get_building_details(datatbl):
    property_types, dwelling_type, construction_type, construction_period, interior, parking = [def_empty_value] * 6
    for dt in datatbl.find_all('dt', text=False):
        try:
            field_name = dt.text.strip()
            value = dt.findNext("dd").text.strip()
            if field_name in ['Type apartment', 'Kind of house', 'Soort appartement', 'Soort woonhuis']:
                property_types = value.replace('appartement', 'apartment').replace('Portiekflat', 'Apartment with shared street entrance').replace('Eengezinswoning, tussenwoning', 'Single-family home, row house').replace('Bovenwoning', 'Upstairs apartment').replace('Galerijflat', 'Gallery flat')
                dwelling_type = property_types.split()
                if len(dwelling_type) > 1:
                    property_types = property_types.replace(dwelling_type[1], '').strip()
                    dwelling_type = dwelling_type[1].replace('(', '').replace(')', '').strip()
            elif field_name in ['Building type', 'Soort bouw']:
                construction_type = value.replace('Nieuwbouw', 'New development')
            elif field_name in ['Type of parking facilities', 'Soort parkeergelegenheid']:
                parking = value.replace('Betaald parkeren, openbaar parkeren en parkeergarage', 'Paid parking, public parking and parking garage')
            elif field_name in ['Year of construction', 'Bouwjaar', 'Construction period', 'Bouwperiode']:
                construction_period = re.compile(r'(\d{4})').search(value)
                construction_period = int(construction_period.group(1)) if construction_period else ''
            elif field_name in ['Specific', 'Specifiek']:
                interior = value.replace('Gestoffeerd','Upholstered').replace('Gemeubileerd', 'Furnished')
            else:
                print(f' + Additional Field has been found: {field_name}')
        except Exception as ex:
            print(f' -- Exception: {field_name}: {ex}')
            continue

    __check_if_variable_assigned({'Property Types':property_types, 'Dwelling Type': dwelling_type,'Construction Type':construction_type, 'Construction Period':construction_period, 'Interior':interior, 'Parking':parking}, def_empty_value)
    return property_types, dwelling_type, construction_type, construction_period, interior, parking


def __get_surface_area(datatbl):
    surface_area, plot_size, volume = [def_empty_value] * 3
    for dt in datatbl.find_all('dt', text=False):
        try:
            field_name = dt.text.strip()
            if field_name == 'Areas' or field_name == 'Gebruiksoppervlakten':
                continue
            value = dt.findNext("dd").text.strip()
            value = int(value.split('m')[0].strip()) if value != '' else ''
            if field_name in ['Living area', 'Wonen']:
                surface_area = value
            elif field_name in ['Exterior space attached to the building', 'Gebouwgebonden buitenruimte']:
                plot_size = value
            elif field_name in ['Volume in cubic meters', 'Inhoud']:
                volume = value
            else:
                print(f' + Additional Field has been found: {field_name}')
        except Exception as ex:
            print(f' -- Exception: {field_name}: {ex}')
            continue

    __check_if_variable_assigned({'Surface Area':surface_area, 'Plot Size':plot_size, 'Volume':volume}, def_empty_value)
    return surface_area, plot_size, volume


def __get_layout(datatbl):
    number_of_rooms, number_of_bedrooms, number_of_bathrooms, number_of_floors, facilities, number_of_stories = [def_empty_value] * 6
    for dt in datatbl.find_all('dt', text=False):
        try:
            field_name = dt.text.strip()
            value = dt.findNext("dd").text.strip()
            if field_name in ['Number of rooms', 'Aantal kamers']:
                room_regex, bed_regex = r"(\d)\s(room(s?))", r"(\d)\s(bedroom(s?))"
                value = value.replace('slaap', 'bed').replace('kamer', 'room')
                number_of_rooms = re.compile(room_regex).search(value)
                number_of_rooms = int(number_of_rooms.group(1)) if number_of_rooms else ''
                number_of_bedrooms = re.compile(bed_regex).search(value)
                number_of_bedrooms = int(number_of_bedrooms.group(1)) if number_of_bedrooms else ''
                # number_of_rooms = int(value.replace('room', '').replace('kamer', '').strip())
            elif field_name in ['Number of bath rooms', 'Aantal badkamers']:
                bath_regex = r"(\d)\s(bathroom(s?))"
                value = value.replace('bad', 'bath').replace('kamer', 'room')
                number_of_bathrooms = re.compile(bath_regex).search(value)
                number_of_bathrooms = int(number_of_bathrooms.group(1)) if number_of_bathrooms else ''
                # number_of_bathrooms = int(value.split('bathroom')[0].split('badkamer')[0].strip())
            elif field_name in ['Located at', 'Gelegen op']:
                number_of_floors = int(value.replace('floor', '').replace('th','').replace('st','').replace('nd','').replace('rd','').replace('woonlaag', '').replace('e', '').strip().replace('Grou', '0'))
            elif field_name in ['Facilities', 'Voorzieningen', 'Bathroom facilities', 'Badkamervoorzieningen']:
                facilities += value.replace('Ligbad', 'Bath').replace('douche', 'shower').replace(' en ', ' and ')
            elif field_name in ['Number of stories', 'Aantal woonlagen']:
                number_of_stories = value.replace('woonlagen', 'stories').replace('zolder', 'attic').replace(' en ', ' and ').replace(' een ',' a ')
            else:
                print(f' + Additional Field has been found: {field_name}')
        except Exception as ex:
            print(f' -- Exception: {field_name}: {ex}')
            continue

    __check_if_variable_assigned({'Number of Rooms':number_of_rooms, 'Number of Bedrooms': number_of_bedrooms, 'Number of Bathrooms':number_of_bathrooms, 'Number of Floors':number_of_floors, 'Facilities':facilities}, def_empty_value)
    return number_of_rooms, number_of_bedrooms, number_of_bathrooms, number_of_floors, facilities


def __get_energy(datatbl):
    energy_level, insulations, heating, hot_water = [def_empty_value] * 4
    for dt in datatbl.find_all('dt', text=False):
        try:
            field_name = dt.text.strip()
            value = dt.findNext("dd").text.strip()
            if field_name in ['Energy label', 'Energielabel']:
                energy_level = value.split('\r\n')[0]
            elif field_name in ['Insulation', 'Isolatie']:
                insulations = value.lower().replace('volledig geïsoleerd', 'Completely insulated').replace('Dakisolatie', 'Roof insulation').replace('muurisolatie', 'wall insulation').replace('vloerisolatie', 'floor insulation').replace(' en ', ' and ').replace('dubbel glas', 'Double glazing').replace('hr-glas', 'HR glass')
            elif field_name in ['Heating', 'Verwarming']:
                heating = value.replace('Stadsverwarming', 'District heating')
            elif field_name in ['Hot water', 'Warm water']:
                hot_water = value.replace('Stadsverwarming', 'District heating')
            else:
                print(f' + Additional Field has been found: {field_name}')
        except Exception as ex:
            print(f' -- Exception: {field_name}: {ex}')
            continue

    __check_if_variable_assigned({'Energy Level':energy_level, 'Insulations':insulations, 'Heating':heating, 'Hot Water':hot_water}, def_empty_value)
    return energy_level, insulations, heating, hot_water


def __get_exterior_space(datatbl):
    sub_description, back_garden, garden_location, garden, balcony = [def_empty_value] * 5
    for dt in datatbl.find_all('dt', text=False):
        try:
            field_name = dt.text.strip()
            value = dt.findNext("dd").text.strip()
            if field_name in ['Location', 'Ligging']:
                sub_description = value.replace('Aan park, aan rustige weg en in woonwijk', 'Alongside park, alongside a quiet road and in residential district')
            elif field_name in ['Back garden', 'Achtertuin']:
                back_garden = value.replace('Balkon aanwezig', 'Yes')
            elif field_name in ['Garden location', 'Ligging tuin']:
                garden_location = value.replace('Gelegen op het zuiden bereikbaar via achterom', 'Located at the south accessible via the rear')
            elif field_name in ['Garden', 'Tuin']:
                garden = value.replace('Achtertuin', 'Yes')
            elif field_name in ['Balcony/roof garden', 'Balkon/dakterras']:
                balcony = value.replace('Balkon aanwezig', 'Balcony present').replace('Balcony present', 'Yes')
            else:
                print(f' + Additional Field has been found: {field_name}')
        except Exception as ex:
            print(f' -- Exception: {field_name}: {ex}')
            continue

    __check_if_variable_assigned({'Sub Description': sub_description, 'Garden':garden, 'Balcony': balcony}, def_empty_value)
    return sub_description, garden, balcony


def __get_parking(datatbl):
    parking = [def_empty_value] * 1
    for dt in datatbl.find_all('dt', text=False):
        try:
            field_name = dt.text.strip()
            value = dt.findNext("dd").text.strip()
            if field_name in ['Type of parking facilities', 'Soort parkeergelegenheid']:
                parking = value.lower().replace(' en ', ' and ').replace('betaald parkeren', 'paid parking').replace('openbaar parkeren', 'public parking').replace('parkeergarage', 'parking garage')
            else:
                print(f' + Additional Field has been found: {field_name}')
        except Exception as ex:
            print(f' -- Exception: {field_name}: {ex}')
            continue

    __check_if_variable_assigned({'Parking':parking}, def_empty_value)
    return parking


def __get_garage(datatbl):
    garage = def_empty_value
    for dt in datatbl.find_all('dt', text=False):
        try:
            field_name = dt.text.strip()
            value = dt.findNext("dd").text.strip()
            if field_name in ['Type of garage', 'Soort garage']:
                garage = value.replace('Parkeerplaats', 'Parking place').replace('Parking place', 'Yes')
            else:
                print(f' + Additional Field has been found: {field_name}')
        except Exception as ex:
            print(f' -- Exception: {field_name}: {ex}')
            continue

    __check_if_variable_assigned({'Garage':garage}, def_empty_value)
    return garage


def __check_if_variable_assigned(vars, def_val):
    [print(f' - {x} not found') for x in vars.keys() if vars[x] == def_val]


def __get_listing_content(url, page):
    # Map items into variables
    details = find_element(page, "div", class_name="object-primary", friendly_name="All Details")
    title = find_element(details, "span", class_name="object-header__title", friendly_name="Title", type_cast="str", attribute='text')
    if title == '':
        return Listing(title='', city='', location='', zip_code='', price='', description='', url=url,
        number_of_rooms='', for_rent_price='', sub_description='', offered_since='', status='', acceptance='', 
        contract_duration='', deposit='', interior='', upkeep='', surface_area='', dwelling_type='', 
        situations='', service_costs='', plot_size='', volume='', property_types='', construction_type='', 
        construction_period='', number_of_bedrooms='', number_of_bathrooms='', number_of_floors='', 
        balcony='', garden='', energy_level='', parking='', listing_type='', garage='', insulations='', storage='', 
        smoking_allowed='', pets_allowed='', broker_link='', broker='', source_found=Sources.Funda, photo_id='')

    print(title)  
    location = find_element(details, "span", class_name="object-header__subtitle", friendly_name="Location", type_cast="str", attribute="text")
    zip_regex = re.compile(r"\d{4}\s([A-Z]{2})\s")
    zip_code = zip_regex.search(location).group(0)
    city = location.replace(zip_code, '').strip('(').strip(')')
    zip_code = zip_code.replace(' ', '')

    description = find_element(details, "div", class_name="object-description-body", friendly_name="Description", type_cast="str", attribute="text", remove_strs=[('\n',' - '), ('\t',' ')])
    neighborhood_section = find_element(page, 'div', class_name="object-buurt", friendly_name="Neighborhood")
    location = find_element(neighborhood_section, 'app-insights-preview-card', class_name=None, friendly_name="Neighborhood Name", custom_name="identifier", type_cast="str", attribute="text")
    location = location.split('/')[1].title()
    
    # Headers
    price_details_available, building_details_available, surface_details_available, layout_details_available, energy_details_available, exterior_details_available, parking_details_available, garage_details_available = [False] * 8

    # Individual Features
    price, deposit, offered_since, contract_duration, status, acceptance = [''] * 6
    property_types, dwelling_type, construction_type, construction_period, interior = [''] * 5
    surface_area, plot_size, volume = [''] * 3
    number_of_rooms, number_of_bedrooms, number_of_bathrooms, number_of_floors, facilities = [''] * 5
    energy_level, insulations, heating, hot_water = [''] * 4
    sub_description, garden, balcony = [''] * 3
    parking, garage = [''] * 2

    data_tables  = details.find_all('dl', {'class': 'object-kenmerken-list'})
    for dl in data_tables:
        header_name = dl.find_previous_sibling('h3').text
        if header_name in ['Overdracht', 'Transfer of ownership']:
            price_details_available = True
            price, deposit, offered_since, contract_duration, status, acceptance = __get_price_details(dl)
        elif header_name in ['Bouw', 'Construction']:
            building_details_available = True
            property_types, dwelling_type, construction_type, construction_period, interior, parking = __get_building_details(dl)
        elif header_name in ['Oppervlakten en inhoud', 'Surface areas and volume']:
            surface_details_available = True
            surface_area, plot_size, volume = __get_surface_area(dl)
        elif header_name in ['Indeling', 'Layout']:
            layout_details_available = True
            number_of_rooms, number_of_bedrooms, number_of_bathrooms, number_of_floors, facilities = __get_layout(dl)
        elif header_name in ['Energie', 'Energy']:
            energy_details_available = True
            energy_level, insulations, heating, hot_water = __get_energy(dl)
        elif header_name in ['Buitenruimte', 'Exterior space']:
            exterior_details_available = True
            sub_description, garden, balcony = __get_exterior_space(dl)
        elif header_name in ['Parkeergelegenheid', 'Parking']:
            parking_details_available = True
            parking = __get_parking(dl)
        elif header_name in ['Garage']:
            garage_details_available = True
            garage = __get_garage(dl)
        else:
            print(f' + Additional Header found: {header_name}')
    
    if not price_details_available: print(f'Price Header are not found')
    if not building_details_available: print(f'Building Header are not found')
    if not surface_details_available: print(f'Surface Header are not found')
    if not layout_details_available: print(f'Layout Header are not found')
    if not energy_details_available: print(f'Energy Header are not found')
    if not exterior_details_available: print(f'Exterior Header are not found')
    if not parking_details_available: print(f'Parking Header are not found')

    brokers = page.find_all("a", {'class':"object-contact-aanbieder-link"})
    broker=[]
    broker_link=[]
    for b in brokers:
        broker.append(b.text)
        broker_link.append(f"{url.split('.nl/')[0]}.nl{b.get('href')}")

    broker = "; ".join(broker)
    broker_link = "; ".join(broker_link)

    #Yet to be mapped:
    for_rent_price, upkeep, situations, service_costs, listing_type, storage, smoking_allowed, pets_allowed, photo_id = [''] * 9

    listing = Listing(
        title=title, city=city, location=location, zip_code=zip_code, price=price, description=description, url=url,
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


def scrape_listing_funda(url, see_window, procnum, return_dict):
    page = initiate_request(url)
    print(f'#### Start: {procnum}: {url}')
    current_listing = __get_listing_content(url, page)
    print(f'#### Complete: {procnum}: {url}')
    return_dict[procnum] = str(current_listing).split('\t')

