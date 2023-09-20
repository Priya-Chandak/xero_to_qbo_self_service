import traceback

from apps.home.data_util import add_job_status
from apps.util.db_mongo import get_mongodb_database

db = get_mongodb_database()
final_bill_1 = db[f"accountright_final_bill_1"]

item_bill = db["accountright_item_bill"].find()
data1 = []
for p1 in item_bill:
    data1.append(p1)

service_bill = db["accountright_service_bill"].find()
data2 = []
for p2 in service_bill:
    data2.append(p2)

professional_bill = db["accountright_professional_bill"].find()
data3 = []
for p3 in professional_bill:
    data3.append(p3)

miscellaneous_bill = db["accountright_miscellaneous_bill"].find()
data4 = []
for p4 in miscellaneous_bill:
    data4.append(p4)

all_bill = db["accountright_all_bill"].find()
data5 = []
for p5 in all_bill:
    data5.append(p5)


def get_accountright_final_bill1(job_id):
    try:
        db = get_mongodb_database()
        final_bill_1 = db[f"accountright_final_bill_1"]

        item_bill = db["accountright_item_bill"].find()
        data1 = []
        for p1 in item_bill:
            data1.append(p1)

        all_bill = db["accountright_all_bill"].find()
        data5 = []
        for p5 in all_bill:
            data5.append(p5)

        for i in range(0, len(data1)):
            for j in range(0, len(data5)):
                if data1[i]["UID"] == data5[j]["UID"]:
                    data5[j].update(data1[i])
                else:
                    pass

        final_bill_1.insert_many(data5)

    except Exception as ex:
        traceback.print_exc()
        


def get_accountright_final_bill2():
    try:
        db = get_mongodb_database()
        final_bill_2 = db[f"accountright_final_bill_2"]

        service_bill = db["accountright_service_bill"].find()
        data2 = []
        for p2 in service_bill:
            data2.append(p2)

        final_bill_1 = db["accountright_final_bill_1"].find()
        data5 = []
        for p5 in final_bill_1:
            data5.append(p5)

        for i in range(0, len(data2)):
            for j in range(0, len(data5)):
                if data2[i]["UID"] == data5[j]["UID"]:
                    data5[j].update(data2[i])
                else:
                    pass

        final_bill_2.insert_many(data5)

    except Exception as ex:
        traceback.print_exc()
        


def get_accountright_final_bill3():
    try:
        db = get_mongodb_database()
        final_bill_3 = db[f"accountright_final_bill_3"]

        professional_bill = db["accountright_professional_bill"].find()
        data3 = []
        for p3 in professional_bill:
            data3.append(p3)

        final_bill_2 = db["accountright_final_bill_2"].find()
        data5 = []
        for p5 in final_bill_2:
            data5.append(p5)

        for i in range(0, len(data3)):
            for j in range(0, len(data5)):
                if data3[i]["UID"] == data5[j]["UID"]:
                    data5[j].update(data3[i])
                else:
                    pass

        final_bill_3.insert_many(data5)

    except Exception as ex:
        traceback.print_exc()
        


def get_accountright_final_bill():
    try:
        db = get_mongodb_database()
        final_bill = db[f"accountright_final_bill"]

        miscellaneous_bill = db["accountright_miscellaneous_bill"].find()
        data4 = []
        for p4 in miscellaneous_bill:
            data4.append(p4)

        final_bill_3 = db["accountright_final_bill_3"].find()
        data5 = []
        for p5 in final_bill_3:
            data5.append(p5)

        for i in range(0, len(data4)):
            for j in range(0, len(data5)):
                if data4[i]["UID"] == data5[j]["UID"]:
                    data5[j].update(data4[i])
                else:
                    pass

        final_bill.insert_many(data5)

        db["accountright_final_bill_1"].drop()
        db["accountright_final_bill_2"].drop()
        db["accountright_final_bill_3"].drop()

    except Exception as ex:
        traceback.print_exc()
        
