# -*- coding: utf-8 -*-
import click
import logging
import pandas as pd
from pathlib import Path
from scrappers.pararius import get_pararius_data
from funda import FundaData, __FundaParseData
from helper import Locations, Sources, get_file_name, file_exists
from dotenv import find_dotenv, load_dotenv


def save_external_data_locally(data: pd.DataFrame, input_location: str, max_price: int, filename: str):
    # FundaData(location=input_location, max_price=max_price, filepath=filename)
    data.to_csv(filename, sep="\t", header=True, index=False) 


def process_data(file_name: str):
    # funda_df = __FundaParseData(pd.read_csv(file_name))
    print()
    # TODO: Fix this


def main(input_location: str, max_price: int):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Making final data set from raw data')

    logger.info('--- Pararius Data')
    pararius_file_name = get_file_name(source=Sources.Pararius, location=input_location)
    
    # TODO: Fix this
    if not file_exists(pararius_file_name):
        pararius_data = get_pararius_data(location=input_location, max_price=max_price)
        save_external_data_locally(data=pararius_data, input_location=input_location, max_price=max_price, filename=pararius_file_name)
    else:
        process_data(pararius_file_name)

    logger.info('--- Funda Data')
    funda_file_name = get_file_name(source=Sources.Funda, location=input_location)
    if not file_exists(funda_file_name):
        save_external_data(input_location=input_location, max_price=max_price, filename=funda_file_name)
    else:
        process_data(funda_file_name)
    return


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main(Locations.Breda.name, 1500)
