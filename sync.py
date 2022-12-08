import GoogleClient
import MongoClient
from Validator import Validator
service = GoogleClient.GoogleClient()
mc = MongoClient.MongoClient()
validator = Validator()

print(validator.is_valid('cartridges', ['2', '2', '3','name', '']))