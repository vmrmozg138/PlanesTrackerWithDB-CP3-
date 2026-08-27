from src.api import APIConnect
from src.file_handler import JsonFileHandler
from src.processor import PlanesProcessor
from src.user_functions import UserFunction
import pathlib

BASE_DIR = pathlib.Path(__file__).parent
file_path_output = BASE_DIR / 'data' / 'planes_output.json'


def user_intreaction():
    country = input("Введите название страны: ")
    top_n = int(input("Введите количество самолетов для вывода в топ N: "))
    filter_words = input("Введите названия стран для фильтрации по стране регистрации: ").split()
    altitude_range = input("Введите диапазон высот полета: ")

    api = APIConnect()

    result = api.get_data(country, 'test-app/1.0')
    print(type(result))

    processor = PlanesProcessor()
    planes = processor.transform_to_objects(result)
    print(type(planes))
    print(len(result))

    uf = UserFunction(planes)
    df = uf.planes_to_dataframe()

    filtered_aeroplanes = uf.filter_planes(df, filter_words)
    print(type(filtered_aeroplanes))
    sorted_aeroplanes = uf.sort_planes(filtered_aeroplanes, ascending=False)

    top_aeroplanes = uf.get_top_planes(sorted_aeroplanes, top_n)

    fh = JsonFileHandler()
    file_path_output.parent.mkdir(parents=True, exist_ok=True)
    planes_data = [p.to_dict() for p in planes]
    fh.write(planes_data, str(file_path_output))

    print(file_path_output)


if __name__ == '__main__':
    user_intreaction()
