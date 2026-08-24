from src.api import APIConnect
from src.processor import PlanesProcessor, Plane

api = APIConnect()

result = api.get_data('Canada', 'test-app/1.0')
print(result)

processor = PlanesProcessor()
planes = processor.transform_to_objects(result)
print(len(planes))
print(len(result))