# from apps.xero.reader.get_static import get_xero_settings
import traceback

from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
import logging

def get_classified_bill(job_id, task_id):
    log_config1=log_config(job_id)
    try:

        db = get_mongodb_database()
        xero_bill = db["xero_bill"].find()
        xero_bill1 = []
        for p1 in xero_bill:
            xero_bill1.append(p1)

        xero_item_bill = db["xero_item_bill"]
        xero_service_bill = db["xero_service_bill"]

        xero_item_bill1 = []
        xero_service_bill1 = []

        for i in range(0, len(xero_bill1)):
            xero_bill1[i].pop("_id")

            for j in range(0, len(xero_bill1[i]["Line"])):
                if "ItemCode" in xero_bill1[i]["Line"][j]:
                    e = {}
                    e["ItemCode"] = xero_bill1[i]["Line"][j]["ItemCode"]
                    if "AccountCode" in xero_bill1[i]["Line"][j]:
                        e["AccountCode"] = xero_bill1[i]["Line"][j]["AccountCode"]
                    xero_item_bill1.append(e)

                elif "ItemCode" not in xero_bill1[i]["Line"][j]:
                    xero_service_bill1.append(xero_bill1[i]["Line"][j])

        if len(xero_item_bill1) > 0:
            db["xero_item_bill"].insert_many(xero_item_bill1)
        if len(xero_service_bill1) > 0:
            db["xero_service_bill"].insert_many(xero_service_bill1)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        traceback.print_exc()
