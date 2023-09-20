import json

path = input("path :")

with open("{}/QBO_COA.json".format(path), "r") as f:
    data = json.load(f)

QuerySet = data

COA_id = []
for i in range(0, len(QuerySet)):
    QuerySet1 = {}
    QuerySet1["Account_Name"] = QuerySet[i]["Name"]
    QuerySet1["Account_Type"] = QuerySet[i]["AccountType"]
    QuerySet1["Bank_Balance"] = QuerySet[i]["CurrentBalance"]
    COA_id.append(QuerySet1)
