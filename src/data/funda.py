import logging
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from funda_scraper import FundaScraper
from dotenv import find_dotenv, load_dotenv


def __FundaParseData(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna("")
    df['price'] = df['price'].str.replace("€", "")
    df['price'] = df['price'].str.replace(".", "")
    df['price'] = df['price'].str.replace(" /mnd", "")
    
    df['size'] = df['size'].str.replace("m²", "")
    
    df['layout'] = df['layout'].str.replace("Aantal kamers", "Number of rooms ")
    df['layout'] = df['layout'].str.replace("Aantal woonlagen", "Number of floors ")
    
    df['living_area'] = df['living_area'].str.replace("m²", "")
    
    df['num_of_rooms'] = df['num_of_rooms'].str.replace(r"kamer(s?)", "", regex=True)
    df['num_of_rooms'] = df['num_of_rooms'].str.replace(r"slaap", "bedroom", regex=True)
    
    df['kind_of_house'] = df['kind_of_house'].str.replace("Bovenwoning", "Upstairs apartment")
    df['kind_of_house'] = df['kind_of_house'].str.replace("portiek", "porch")
    df['kind_of_house'] = df['kind_of_house'].str.replace("Portiekflat (souterrain)", "Porch flat (basement)")
    df['kind_of_house'] = df['kind_of_house'].str.replace("Eengezinswoning", "Single-family home")
    df['kind_of_house'] = df['kind_of_house'].str.replace("hoekwoning", "corner house")
    df['kind_of_house'] = df['kind_of_house'].str.replace("Opslagruimte", "Storage area")
    df['kind_of_house'] = df['kind_of_house'].str.replace("Opslagruimte", "Storage area")
    df['kind_of_house'] = df['kind_of_house'].str.replace("Parkeerplaats", "Parking spot")
    df['kind_of_house'] = df['kind_of_house'].str.replace("Galerijflat", "Gallery flat")
    df['kind_of_house'] = df['kind_of_house'].str.replace("tussenwoning", "terraced house")
    df['kind_of_house'] = df['kind_of_house'].str.replace("Portiekwoning", "Porch house")
    
    return df


def FundaData(location: str, max_price: int, filepath: str, is_raw: bool=True) -> pd.DataFrame:
    scraper = FundaScraper(area=location.lower(), want_to="rent", find_past=False, min_price=0, max_price=max_price, page_start=1, n_pages=100)
    df = scraper.run(raw_data=is_raw, save=True, filepath=filepath)
    return df


