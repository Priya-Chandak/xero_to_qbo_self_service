import json
import traceback
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo, get_start_end_dates_of_job
from time import sleep


def add_bank_transfer1(job_id, task_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(
            job_id)
        url = f"{base_url}/transfer?minorversion={minorversion}"
        mongo_database = get_mongodb_database()
        bank_transfer = mongo_database["bank_transfer"].find(
            {"job_id": job_id})
        QuerySet1 = []
        for p1 in bank_transfer:
            QuerySet1.append(p1)

        QBO_COA = mongo_database["QBO_COA"].find({"job_id": job_id})
        QBO_coa = []
        for p2 in QBO_COA:
            QBO_coa.append(p2)


        QuerySet1=QuerySet1
        for i in range(0, len(QuerySet1)):
            print(i)
            FromAccountRef = {}
            ToAccountRef = {}
            for j1 in range(0, len(QBO_coa)):
                if (
                        QuerySet1[i]["FromAccountName"].lower().strip()
                        == QBO_coa[j1]["Name"].lower().strip()
                ):
                    FromAccountRef["name"] = QBO_coa[j1]["Name"]
                    FromAccountRef["value"] = QBO_coa[j1]["Id"]

                if (
                        QuerySet1[i]["ToAccountName"].lower().strip()
                        == QBO_coa[j1]["Name"].lower().strip()
                ):
                    ToAccountRef["name"] = QBO_coa[j1]["Name"]
                    ToAccountRef["value"] = QBO_coa[j1]["Id"]

            _id=QuerySet1[i]['_id']
            task_id=QuerySet1[i]['task_id']
                
            QuerySet2 = {"Amount": QuerySet1[i]["Amount"],
                         "PrivateNote": QuerySet1[i]["Memo"] + "-" + QuerySet1[i]["TransferNumber"]
                         if QuerySet1[i]["Memo"] is not None else
                         QuerySet1[i]["TransferNumber"], "TxnDate": QuerySet1[i]["Date"],
                         "FromAccountRef": FromAccountRef, "ToAccountRef": ToAccountRef}
            payload = json.dumps(QuerySet2)
            bank_transfer_date = QuerySet1[i]["Date"][0:10]
            bank_transfer_date1 = datetime.strptime(
                bank_transfer_date, "%Y-%m-%d")
            
            id_or_name_value_for_error = (
                QuerySet1[i]["TransferNumber"]
                if QuerySet1[i]["TransferNumber"] is not None
                else ""
            )
            if start_date1 != "" and end_date1 != "":
                if (bank_transfer_date1 >= start_date1) and (
                        bank_transfer_date1 <= end_date1
                ):
                    post_data_in_qbo(
                        url, headers, payload,mongo_database["bank_transfer"],_id, job_id,task_id, id_or_name_value_for_error
                    )
            else:
                post_data_in_qbo(
                        url, headers, payload,mongo_database["bank_transfer"],_id, job_id,task_id, id_or_name_value_for_error
                    )
        
    except Exception as ex:
        traceback.print_exc()


import json
import traceback
from datetime import datetime
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo, get_start_end_dates_of_job
from time import sleep


def add_bank_transfer(job_id, task_id):
    try:
        start_date1, end_date1 = get_start_end_dates_of_job(job_id)
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/transfer?minorversion={minorversion}"
        mongo_database = get_mongodb_database()

        bank_transfer_data = {}
        QBO_coa_data = {}

        for data in mongo_database["bank_transfer"].find({"job_id": job_id}):
            bank_transfer_data[data["_id"]] = data

        for data in mongo_database["QBO_COA"].find({"job_id": job_id}):
            QBO_coa_data[data["Name"].lower().strip()] = data

        for _id, bank_transfer in bank_transfer_data.items():
            print(_id)
            FromAccountRef = {}
            ToAccountRef = {}

            FromAccountName = bank_transfer["FromAccountName"].lower().strip()
            if FromAccountName in QBO_coa_data:
                FromAccountRef["name"] = QBO_coa_data[FromAccountName]["Name"]
                FromAccountRef["value"] = QBO_coa_data[FromAccountName]["Id"]

            ToAccountName = bank_transfer["ToAccountName"].lower().strip()
            if ToAccountName in QBO_coa_data:
                ToAccountRef["name"] = QBO_coa_data[ToAccountName]["Name"]
                ToAccountRef["value"] = QBO_coa_data[ToAccountName]["Id"]

            task_id = bank_transfer["task_id"]

            QuerySet2 = {
                "Amount": bank_transfer["Amount"],
                "PrivateNote": bank_transfer["Memo"] + "-" + bank_transfer["TransferNumber"]
                if bank_transfer["Memo"] is not None
                else bank_transfer["TransferNumber"],
                "TxnDate": bank_transfer["Date"],
                "FromAccountRef": FromAccountRef,
                "ToAccountRef": ToAccountRef
            }

            payload = json.dumps(QuerySet2)
            bank_transfer_date = bank_transfer["Date"][0:10]
            bank_transfer_date1 = datetime.strptime(bank_transfer_date, "%Y-%m-%d")

            id_or_name_value_for_error = bank_transfer["TransferNumber"] if bank_transfer["TransferNumber"] is not None else ""

            if start_date1 != "" and end_date1 != "":
                if bank_transfer_date1 >= start_date1 and bank_transfer_date1 <= end_date1:
                    post_data_in_qbo(url, headers, payload, mongo_database["bank_transfer"], _id, job_id, task_id, id_or_name_value_for_error)
            else:
                post_data_in_qbo(url, headers, payload, mongo_database["bank_transfer"], _id, job_id, task_id, id_or_name_value_for_error)

    except Exception as ex:
        traceback.print_exc()
