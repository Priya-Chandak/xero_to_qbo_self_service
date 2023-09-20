import json

from pymongo import MongoClient

# Making Connection
myclient = MongoClient("mongodb://localhost:27017/")

# database
db = myclient["MMC-Convert"]

filenames = [
    "all_bill",
    "all_invoices",
    "chart_of_account",
    "classified_COA",
    "combined_bill",
    "customer",
    "employee",
    "item_bill",
    "item_invoice",
    "item",
    "job",
    "journal",
    "misc_bill",
    "professional_bill",
    "received_money",
    "service_bill",
    "spend_money",
    "supplier",
    "taxcode",
    "trial_balance",
]

path = input("Enter a path for your MYOB json data files:")

# Created or Switched to collection
for i in range(0, len(filenames)):
    Collection = db[filenames[i]]
    with open("{}/{}.json".format(path, filenames[i]), "r") as file:
        file_data = json.load(file)

    # if JSON contains data more than one entry
    # insert_many is used else inser_one is used
    if isinstance(file_data, list):
        Collection.insert_many(file_data)
    else:
        Collection.insert_one(file_data)
