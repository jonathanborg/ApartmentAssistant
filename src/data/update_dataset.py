# -*- coding: utf-8 -*-
import click
import logging
import pandas as pd
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from funda import FundaData, __FundaParseData
from scrappers.pararius import get_pararius_data
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
    old_listings = []
    if len(active_listings) > 0:
        headers = active_listings.pop(0)
        old_listings += pd.DataFrame(active_listings, columns=headers)['Url'].tolist()
    if len(dated_listings) > 0:
        headers = dated_listings.pop(0)
        old_listings += pd.DataFrame(dated_listings, columns=headers)['Url'].tolist()
    if len(old_listings) == 0:
        return None, active_listings, dated_listings
    return old_listings, active_listings, dated_listings


def get_new_listings(input_location: str, max_price: int, old_listings_urls: list, save_local_files: bool) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    logger.info('--- Getting New Pararius Data')
    pararius_file_name = get_file_name(source=Sources.Pararius, location=input_location)
    if (old_listings_urls is None or len(old_listings_urls) == 0) and file_exists(pararius_file_name):
        old_listings_urls = get_data_from_file(pararius_file_name)['Url']
        old_listings_urls = None if old_listings_urls.empty else old_listings_urls
    pararius_data = get_pararius_data(location=input_location, max_price=max_price, old_listings_urls=old_listings_urls)
    if save_local_files:
        save_data_to_file(data=pararius_data, input_location=input_location, max_price=max_price, filename=pararius_file_name)
    
    logger.info('--- Getting New Funda Data')
    # funda_file_name = get_file_name(source=Sources.Funda, location=input_location)
    # TODO: Implement Funda Scrapper without library
    funda_data = None
    # if save_local_files:
    #     save_data_to_file(data=funda_data, input_location=input_location, max_price=max_price, filename=funda_file_name)
    return pd.concat([pararius_data, funda_data])


def main(input_location: str, max_price: int, save_local_files: bool=False):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Making final data set from raw data')

    logger.info('- Getting Past Data')
    old_listings, active_listings, dated_listings = get_previous_listings()
    
    logger.info('- Getting New Listings')
    new_listings = get_new_listings(input_location=input_location, max_price=max_price, old_listings_urls=old_listings, save_local_files=save_local_files)

    logger.info('- Upload New Listings')
    listings_input = new_listings.values.tolist() if len(active_listings) > 0 else [new_listings.columns.tolist()] + new_listings.values.tolist()
    if len(listings_input) > 0:
        api_call = google_call(call_type=CallType.Write, sheet_id=SPREADSHEET_ID, sheet_range=f"{SHEET_REVIEW_NAME}!{sheet_range_split[0]}{len(active_listings)+1}:{sheet_range_split[1]}", additional_data=listings_input)
    


# def process_data(file_name: str):
#     # funda_df = __FundaParseData(pd.read_csv(file_name))
#     print()
#     # TODO: Fix this


# def main(input_location: str, max_price: int):
#     """ Runs data processing scripts to turn raw data from (../raw) into
#         cleaned data ready to be analyzed (saved in ../processed).
#     """
#     logger = logging.getLogger(__name__)
#     logger.info('Making final data set from raw data')

#     logger.info('--- Pararius Data')
#     pararius_file_name = get_file_name(source=Sources.Pararius, location=input_location)


#     # TODO: Fix this
#     if not file_exists(pararius_file_name):
#         pararius_data = get_pararius_data(location=input_location, max_price=max_price)
#         save_data_to_file(data=pararius_data, input_location=input_location, max_price=max_price, filename=pararius_file_name)
#     else:
#         process_data(pararius_file_name)

#     logger.info('--- Funda Data')
#     funda_file_name = get_file_name(source=Sources.Funda, location=input_location)
#     if not file_exists(funda_file_name):
#         save_external_data(input_location=input_location, max_price=max_price, filename=funda_file_name)
#     else:
#         process_data(funda_file_name)
#     return


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
    save_local_files = True
    main(Locations.Roosendaal.name, 1500, save_local_files)
