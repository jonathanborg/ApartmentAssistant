import os.path
import datetime
import pandas as pd
from enum import Enum


def __get_file_path() -> str:
    return "./data/external/"


def get_file_name(source: Enum, location: str) -> str:
    today_str = datetime.datetime.today().strftime('%Y%m%d')
    # today_str = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    directory = f'{__get_file_path()}{location}/' 
    output = f'{directory}{source.name}_{today_str}.csv'.lower()
    os.makedirs(os.path.dirname(directory), exist_ok=True)
    return output


def file_exists(file_path):
    return os.path.isfile(file_path)


def get_data_from_file(file_name: str, has_headers: bool=True, sep: str='\t') -> pd.DataFrame:
    if has_headers:
        return pd.read_csv(file_name, sep=sep, header=0)
    return pd.read_csv(file_name, sep=sep)


def save_data_to_file(data: pd.DataFrame, input_location: str, max_price: int, filename: str):
    # FundaData(location=input_location, max_price=max_price, filepath=filename)
    data.to_csv(filename, sep="\t", header=True, index=False) 
