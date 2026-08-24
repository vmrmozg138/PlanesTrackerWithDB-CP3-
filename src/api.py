from abc import ABC, abstractmethod
from requests import get

class API(ABC):

    @abstractmethod
    def get_data(self):
        pass

class APIConnect(API):

    def __init__(self):
        self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.opensky_url = 'https://opensky-network.org/api/states/all?'
        self.country = ''
        self.useragent = ''
        self.params = {
            'country': '',
            'format': 'json',
            'limit': 1,
        }
        self.headers = {'User-Agent': ''}



    def get_data(self, country: str, useragent: str):
        self.country = country
        self.useragent = useragent
        self.params['country'] = country
        self.headers['User-Agent'] = useragent

        response = get(self.openstreetmap_url, params=self.params, headers=self.headers)
        data = response.json()

        coordinates = data[0].get('boundingbox')

        opensky_params = {
            'lamin': coordinates[0],
            'lamax': coordinates[1],
            'lomin': coordinates[2],
            'lomax': coordinates[3],
        }

        response_os = get(self.opensky_url, params=opensky_params, headers=self.headers)

        planes = response_os.json()
        return planes["states"]











