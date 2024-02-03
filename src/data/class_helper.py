import datetime
from enum import Enum


class Sources(Enum):
    Funda=1,
    Pararius=2


class Locations(Enum):
    Breda=1,
    Roosendaal=2


class ListingProp(Enum):
    Title=1,
    Location=2,
    Price=3,
    Url=4,

    Area=5,
    Room=6,
    Interior=7,

    Address=8,
    Zip_Code=9,
    City=10,
    Description=11,

    Available_Since=12,
    Type_of_Property=13,
    Building_Type=14,
    Number_of_Rooms=15,
    Number_of_Bathrooms=16,
    Energy_Level=17,
    Year=18,
    Size=19,
    Parking=20,

    Photo=21,
    Property_External_Url=22,
    Brokerage_Firm=23,
    Brokerage_Firm_link=24,
    Log_Id=25,


class Listing():
    def __init__(self, 
        title: str, city: str, location: str, zip_code: str, price: int, description: str, url: str,
        number_of_rooms: int, for_rent_price: int, sub_description: str, offered_since: datetime, 
        status: str, acceptance: datetime, contract_duration: str, deposit: int, interior: str, upkeep: str, 
        surface_area: int, dwelling_type: str, situations: str, 
        service_costs: int, plot_size: int, volume: int, property_types: str, construction_type: str, 
        construction_period: int, number_of_bedrooms: int, number_of_bathrooms: int, number_of_floors: int, 
        balcony: bool, garden: bool, energy_level: str, parking: bool, listing_type: str, garage: bool, 
        insulations: bool, storage: bool, available: str, smoking_allowed: bool, pets_allowed: bool, 
        broker_link: str, broker: str, photo_id: str=None
    ):
        self.title, self.city, self.location, self.zip_code, self.price, self.description, self.url = title, city, location, zip_code, price, description, url
        self.number_of_rooms, self.interior, self.for_rent_price, self.sub_description, self.offered_since = number_of_rooms, interior, for_rent_price, sub_description, offered_since
        self.status, self.acceptance, self.contract_duration, self.deposit, self.interior, self.upkeep = status, acceptance, contract_duration, deposit, interior, upkeep
        self.surface_area, self.dwelling_type, self.situations = surface_area, dwelling_type, situations
        self.service_costs, self.plot_size, self.volume, self.property_types, self.construction_type = service_costs, plot_size, volume, property_types, construction_type
        self.construction_period, self.number_of_bedrooms, self.number_of_bathrooms, self.number_of_floors = construction_period, number_of_bedrooms, number_of_bathrooms, number_of_floors
        self.balcony, self.garden, self.energy_level, self.parking, self.listing_type, self.garage = balcony, garden, energy_level, parking, listing_type, garage
        self.insulations, self.storage, self.available, self.smoking_allowed, self.pets_allowed = insulations, storage, available, smoking_allowed, pets_allowed
        self.broker_link, self.broker, self.photo_id = broker_link, broker, photo_id
        self.internal_id = None

    @staticmethod
    def header():
        # Main Details
        main_dets = f'Title, City, Location, Price, Description, Url, Property Type, Zip Code, Interior, Available From' 
        # Contract Details
        contract_dets = f'Contract Duration, Deposit, Service Costs, Rent Price, Sub Description, Offered_since, Surface Area, Number of Rooms, Energy Level, Status, Available, Upkeep, Dwelling Type'
        # Construction Details
        constr_dets = f'Situations, Plot Size, Volume, Construction Type, Construction Period' 
        # Building Details
        build_dets = f'Number of Bedrooms, Number of Bathrooms, Number of Floors, Balcony, Garden, Storage, Parking, Listing Type, Garage, Insulations, Smoking Allowed, Pets Allowed'
        # Broker Details
        brk_dets = f'Broker Link, Broker, Photo Id, Internal Id'
        return f'{main_dets}, {contract_dets}, {constr_dets}, {build_dets}, {brk_dets}'


    def __repr__(self):
        return f"{self.title}\t{self.city}\t{self.location}\t{self.price}\t{self.description}\t{self.url}\t{self.property_types}\t{self.zip_code}\t{self.interior}\t{self.acceptance}\t{self.contract_duration}\t{self.deposit}\t{self.service_costs}\t{self.for_rent_price}\t{self.sub_description}\t{self.offered_since}\t{self.surface_area}\t{self.number_of_rooms}\t{self.energy_level}\t{self.status}\t{self.available}\t{self.upkeep}\t{self.dwelling_type}\t{self.situations}\t{self.plot_size}\t{self.volume}\t{self.construction_type}\t{self.construction_period}\t{self.number_of_bedrooms}\t{self.number_of_bathrooms}\t{self.number_of_floors}\t{self.balcony}\t{self.garden}\t{self.storage}\t{self.parking}\t{self.listing_type}\t{self.garage}\t{self.insulations}\t{self.smoking_allowed}\t{self.pets_allowed}\t{self.broker_link}\t{self.broker}\t{self.photo_id}\t{self.internal_id}"
