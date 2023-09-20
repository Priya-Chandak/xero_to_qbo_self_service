import traceback

from apps.home.data_util import add_job_status
from apps.util.db_mongo import get_mongodb_database


def get_accountright_combined_bill(data1, all_bill, k, job_id):
    try:
        db = get_mongodb_database()
        item_bill = db["accountright_item_bill"]
        service_bill = db["accountright_service_bill"]
        misc_bill = db["accountright_misc_bill"]
        professional_bill = db["accountright_professional_bill"]
        all_bill = db["accountright_all_bill"]

        x1 = item_bill.find()
        x2 = service_bill.find()
        x3 = misc_bill.find()
        x4 = professional_bill.find()
        x5 = all_bill.find()

        data1 = []
        data2 = []
        data3 = []
        data4 = []
        data5 = []

        for p1 in x1:
            data1.append(p1)
        for p2 in x2:
            data2.append(p2)
        # for p3 in x3:
        #     data3.append(p3)
        # for p4 in x4:
        #     data4.append(p4)
        for p5 in x5:
            data5.append(p5)

        combined_bill = db[f"accountright_combined_bill_{k}"]

        for p in range(0, len(data1)):
            for q in range(0, len(data5)):
                if data1[p]["UID"] == data5[q]["UID"]:
                    data5[q].update(data1[p])
                else:
                    pass

        combined_bill.insert_many(data5)
        combined_bill1 = combined_bill.find()
        data6 = []
        for p6 in combined_bill1:
            data6.append(p6)
        get_data2(data2, data6, 2)
    except Exception as ex:
        traceback.print_exc()
        


def get_data2(data1, data5, k, job_id):
    db = get_mongodb_database()
    combined_bill = db[f"combined_bill_{k}"]

    for p in range(0, len(data1)):
        for q in range(0, len(data5)):
            if data1[p]["UID"] == data5[q]["UID"]:
                data5[q].update(data1[p])
            else:
                pass

    combined_bill.insert_many(data5)
    combined_bill2 = combined_bill.find()
    data6 = []
    for p6 in combined_bill2:
        data6.append(p6)
    get_data3(data1, data6, 3)


def get_data3(data1, data5, k, job_id):
    db = get_mongodb_database()
    combined_bill = db[f"combined_bill_{k}"]

    for p in range(0, len(data1)):
        for q in range(0, len(data5)):
            if data1[p]["UID"] == data5[q]["UID"]:
                data5[q].update(data1[p])
            else:
                pass

    combined_bill.insert_many(data5)
    combined_bill3 = combined_bill.find()
    data6 = []
    for p6 in combined_bill3:
        data6.append(p6)
    get_data4(data1, data6, 4)


def get_data4(data1, data5, k, job_id):
    db = get_mongodb_database()
    combined_bill = db[f"combined_bill_{k}"]

    for p in range(0, len(data1)):
        for q in range(0, len(data5)):
            if data1[p]["UID"] == data5[q]["UID"]:
                data5[q].update(data1[p])
            else:
                pass

    combined_bill.insert_many(data5)
