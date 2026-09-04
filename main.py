from src.api import APIConnect
from src.file_handler import JsonFileHandler
from src.processor import PlanesProcessor
from src.user_functions import UserFunction
import pathlib
from src.db_manager import DBManager
from src.config import config

BASE_DIR = pathlib.Path(__file__).parent
file_path_output = BASE_DIR / 'data' / 'planes_output.json'


def user_intreaction():
    countries = input("Введите названия стран через пробелы для отслеживания самолетов(не менее 4):").split()

    while len(countries) < 4:
        add_countries = input(f"Вы ввели {len(countries)}, но надо еще хотя бы {4 - len(countries)}: ").split()
        countries.extend(add_countries)

    print(countries)

    api = APIConnect()

    planes_in_countries = []

    for index, country in enumerate(countries):
        result = api.get_data(country, 'test-app/1.0')
        processor = PlanesProcessor()
        planes = processor.transform_to_objects(result)
        uf = UserFunction(planes)
        df = uf.planes_to_dataframe()
        planes_in_countries.append({'country_id': index + 1, 'country_name': country, 'data': df})

    db_manager = DBManager()
    db_manager.connect(config())

    db_manager.write_once(planes_in_countries)

    df1 = db_manager.get_countries_and_aeroplanes_count()

    df2 = db_manager.get_aeroplanes_with_higher_speed()

    df3 = db_manager.get_aeroplanes_with_keyword('sa')

    print(df1)

    print(df2)

    print(df3)


if __name__ == '__main__':
    user_intreaction()


