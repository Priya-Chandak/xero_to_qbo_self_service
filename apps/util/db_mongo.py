import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_mongodb_database():
    client = MongoClient(os.getenv("URL"))
    return client["MMC"]


def get_mongodb_database():
    CONNECTION_STRING = os.getenv("URL")
    client = MongoClient(CONNECTION_STRING)
    return client["MMC"]

def post_data_to_myob(url,payload):
    print("Posting data to myob")
