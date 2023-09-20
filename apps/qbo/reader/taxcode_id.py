import json

path = input("path :")

with open("{}/QBO_taxcode.json".format(path), "r") as f:
    data = json.load(f)

QuerySet = data["QueryResponse"]["TaxCode"]

taxcode_id = []
for i in range(0, len(QuerySet)):
    QuerySet1 = {}
    QuerySet1["ID"] = QuerySet[i]["Id"]
    QuerySet1["Name"] = QuerySet[i]["Name"]

    taxcode_id.append(QuerySet1)

"""
Available TaxCode : 
[{'ID': 'TAX', 'Name': 'TAX'}, {'ID': 'NON', 'Name': 'NON'}, 
{'ID': 'CustomSalesTax', 'Name': 'CustomSalesTax'}, 
{'ID': '2', 'Name': 'California'}, {'ID': '3', 'Name': 'Tucson'}]
"""
