# -*- coding: utf-8 -*-
import click
import logging
import pandas as pd
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
# from funda import FundaData, __FundaParseData
from scrappers.helper import get_website_data

# from scrappers.pararius import get_pararius_data
# from scrappers.funda import get_funda_data
from class_helper import Locations, Sources, Listing
from func_helper import get_file_name, file_exists, save_data_to_file, get_data_from_file
from integration.sheets import google_call
from integration.helpers import CallType
from integration.config import SPREADSHEET_ID, SHEET_RANGE, SHEET_REVIEW_NAME, SHEET_DEAD_NAME

sheet_range_split = f"{SHEET_RANGE}{chr(ord('@')+len(Listing.header().split(', ')))}".split(':')


def one_time_sheets_import(file_name):
    all_applications = get_data_from_file(file_name)
    applications = [all_applications.columns.tolist()] + all_applications.values.tolist()
    call_api = google_call(call_type=CallType.Write, sheet_id=SPREADSHEET_ID, sheet_range=f"{SHEET_REVIEW_NAME}!{sheet_range_split[0]}{1}:{sheet_range_split[1]}", additional_data=applications)
    return call_api


def get_previous_listings() -> pd.DataFrame:
    active_listings = google_call(call_type=CallType.Read, sheet_id=SPREADSHEET_ID, sheet_range=f"{SHEET_REVIEW_NAME}!{sheet_range_split[0]}1:{sheet_range_split[1]}")
    dated_listings = google_call(call_type=CallType.Read, sheet_id=SPREADSHEET_ID, sheet_range=f"{SHEET_DEAD_NAME}!{sheet_range_split[0]}1:{sheet_range_split[1]}")
    old_listings, new_listings = [], None
    if len(active_listings) > 0:
        headers = active_listings.pop(0)
        act_rows = pd.DataFrame(active_listings, columns=headers)
        old_listings += act_rows[act_rows['Date Found'] != '']['URL'].tolist()
        new_listings = act_rows[act_rows['Date Found'] == '']['URL'].tolist()
    if len(dated_listings) > 0:
        headers = dated_listings.pop(0)
        old_listings += pd.DataFrame(dated_listings, columns=headers)['URL'].tolist()
    if len(old_listings) == 0:
        old_listings = None
    return old_listings, new_listings, active_listings, dated_listings


# def get_new_listings_per_source(source: Sources, input_location: str, max_price: int, max_radius: int, old_listings_urls: list, new_listings_urls: list, save_local_files: bool, use_selenium: bool, see_window: bool) -> pd.DataFrame:
#     logger = logging.getLogger(__name__)
#     logger.info(f'--- Getting New {source.name} Data')
#     source_data = get_website_data(source=source, location=input_location, max_price=max_price, max_radius=max_radius, old_listings_urls=old_listings_urls, new_listings_urls=new_listings_urls, use_selenium=use_selenium, see_window=see_window)
#     if save_local_files:
#         source_file_name = get_file_name(source=source, location=input_location)
#         save_data_to_file(data=source_data, input_location=input_location, max_price=max_price, filename=pararius_file_name)
#     return source_data
# def get_new_listings(input_location: str, max_price: int, max_radius: int, old_listings_urls: list, new_listings_urls: list, save_local_files: bool, see_window: bool) -> pd.DataFrame:
#     logger = logging.getLogger(__name__)
#     pararius_data = get_new_listings_per_source(source=Sources.Pararius, input_location=input_location, max_price=max_price, max_radius=max_radius, old_listings_urls=old_listings_urls, new_listings_urls=new_listings_urls, save_local_files=save_local_files, use_selenium=True, see_window=see_window)
#     funda_data = get_new_listings_per_source(source=Sources.Funda, input_location=input_location, max_price=max_price, max_radius=max_radius, old_listings_urls=old_listings_urls, new_listings_urls=new_listings_urls, save_local_files=save_local_files, use_selenium=False, see_window=False)
#     # pararius_data, funda_data = None, None
#     rentola_data = get_new_listings_per_source(source=Sources.Rentola, input_location=input_location, max_price=max_price, max_radius=max_radius, old_listings_urls=old_listings_urls, new_listings_urls=new_listings_urls, save_local_files=save_local_files, use_selenium=False, see_window=False)
#     return pd.concat([pararius_data, funda_data, rentola_data])
# def main(input_location: str, max_price: int, max_radius: int, save_local_files: bool=False, see_window: bool=False):
#     """ Runs data processing scripts to turn raw data from (../raw) into
#         cleaned data ready to be analyzed (saved in ../processed).
#     """
#     logger = logging.getLogger(__name__)
#     logger.info('Making final data set from raw data')
#     logger.info('- Getting Past Data')
#     old_listings, new_listings, active_listings, dated_listings = get_previous_listings()
#     logger.info('- Getting New Listings')
#     new_listings = get_new_listings(input_location=input_location, max_price=max_price, max_radius=max_radius, old_listings_urls=old_listings, new_listings_urls=new_listings, save_local_files=save_local_files, see_window=see_window)
#     logger.info('- Upload New Listings')
#     listings_input = new_listings.values.tolist() if len(active_listings) > 0 else [new_listings.columns.tolist()] + new_listings.values.tolist()
#     if len(listings_input) > 0:
#         api_call = google_call(call_type=CallType.Write, sheet_id=SPREADSHEET_ID, sheet_range=f"{SHEET_REVIEW_NAME}!{sheet_range_split[0]}{len(active_listings)+1}:{sheet_range_split[1]}", additional_data=listings_input)
  
def get_new_listings_per_source(source: Sources, input_locations: dict, max_price: int, old_listings_urls: list, new_listings_urls: list, save_local_files: bool, use_selenium: bool, see_window: bool, get_new_data: bool) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    logger.info(f'--- Getting New {source.name} Data')
    source_data = get_website_data(source=source, locations=input_locations, max_price=max_price, old_listings_urls=old_listings_urls, new_listings_urls=new_listings_urls, use_selenium=use_selenium, see_window=see_window, get_new_data=get_new_data)
    if save_local_files:
        source_file_name = get_file_name(source=source, location=input_location)
        save_data_to_file(data=source_data, input_location=input_location, max_price=max_price, filename=pararius_file_name)
    return source_data

def get_new_listings(input_locations: dict, max_price: int, old_listings_urls: list, new_listings_urls: list, save_local_files: bool, see_window: bool, get_new_data: bool) -> pd.DataFrame:
    # pararius_data, funda_data = None, None
    pararius_data = get_new_listings_per_source(source=Sources.Pararius, input_locations=input_locations, max_price=max_price, old_listings_urls=old_listings_urls, new_listings_urls=new_listings_urls, save_local_files=save_local_files, use_selenium=True, see_window=see_window, get_new_data=get_new_data)
    funda_data = get_new_listings_per_source(source=Sources.Funda, input_locations=input_locations, max_price=max_price, old_listings_urls=old_listings_urls, new_listings_urls=new_listings_urls, save_local_files=save_local_files, use_selenium=False, see_window=False, get_new_data=get_new_data)
    # rentola_data = get_new_listings_per_source(source=Sources.Rentola, input_locations=input_locations, max_price=max_price, old_listings_urls=old_listings_urls, new_listings_urls=new_listings_urls, save_local_files=save_local_files, use_selenium=False, see_window=False, get_new_data=get_new_data)
    rentola_data = None
    return pd.concat([pararius_data, funda_data, rentola_data])

  

def main(run_details: dict):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Making final data set from raw data')

    logger.info('- Getting Past Data')
    old_listings, new_listings, active_listings, dated_listings = get_previous_listings()
    
    logger.info('- Getting New Listings')
    setup_dets = run_details['setup']
    max_price, scrap_data = setup_dets['price'], setup_dets['new_data']
    save_local_files, see_window = setup_dets['save_file'], setup_dets['see_selenium']
    new_listings = get_new_listings(input_locations=run_details['localities'], max_price=max_price, old_listings_urls=old_listings, new_listings_urls=new_listings, save_local_files=save_local_files, see_window=see_window, get_new_data=scrap_data)

    logger.info('- Upload New Listings')
    listings_input = new_listings.values.tolist() if len(active_listings) > 0 else [new_listings.columns.tolist()] + new_listings.values.tolist()
    if len(listings_input) > 0:
        api_call = google_call(call_type=CallType.Write, sheet_id=SPREADSHEET_ID, sheet_range=f"{SHEET_REVIEW_NAME}!{sheet_range_split[0]}{len(active_listings)+1}:{sheet_range_split[1]}", additional_data=listings_input)
    return

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    # pararius_file_name = get_file_name(source=Sources.Pararius, location=Locations.Roosendaal.name)
    # one_time_sheets_import(pararius_file_name)
    save_local_files = False
    see_selenium = True
    get_new_data = True
    details={
        'setup':{
            'price':1750, 
            'new_data':get_new_data,
            'save_file': save_local_files,
            'see_selenium':see_selenium
        },
        'localities':{
            Locations.Dordrecht.name: 2,
            Locations.Roosendaal.name: 5,
            Locations.Barendrecht.name: 5
        }
    }
    main(details)
    # main(Locations.Dordrecht.name, 1500, 2, save_local_files, see_selenium)
    # main(Locations.Roosendaal.name, 1500, 5, save_local_files, see_selenium)
    # main(Locations.Barendrecht.name, 1500, 5, save_local_files, see_selenium)
