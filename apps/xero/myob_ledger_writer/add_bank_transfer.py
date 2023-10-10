import asyncio
import json

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_bank_transfer_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        tool1 = aliased(Tool)
        tool2 = aliased(Tool)

        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        xero_bank_transfer1 = dbname['xero_bank_transfer']
        chart_of_account1 = dbname['chart_of_account']

        Transfer = []
        for k in xero_bank_transfer1.find({'job_id': job_id}):
            Transfer.append(k)

        account = []
        for p in chart_of_account1.find({'job_id': job_id}):
            account.append(p)

        for i1 in range(0, len(Transfer)):
            _id = Transfer[i1]['_id']
            task_id = Transfer[i1]['task_id']
            QuerySet1 = {}
            QuerySet2 = {}
            QuerySet3 = {}
            QuerySet1["Amount"] = Transfer[i1]["Amount"]
            QuerySet1["Date"] = Transfer[i1]["Date"][0:10]
            if 'Memo' in Transfer[i1]:
                QuerySet1["Memo"] = Transfer[i1]["Memo"]
            QuerySet1["TransferNumber"] = Transfer[i1]["TransferNumber"][-5:]

            for i2 in range(0, len(account)):

                if Transfer[i1]["FromAccountName"].lower().strip() == account[i2]["Name"].lower().strip():
                    QuerySet2['UID'] = account[i2]["UID"]
                    QuerySet2['Name'] = account[i2]["Name"]
                    break
                elif Transfer[i1]["FromAccountID"] == account[i2]["DisplayId"]:
                    QuerySet2['UID'] = account[i2]["UID"]
                    QuerySet2['Name'] = account[i2]["Name"]
                    break
            for i3 in range(0, len(account)):
                if Transfer[i1]["ToAccountName"].lower().strip() == account[i3]["Name"].lower().strip():
                    QuerySet3['UID'] = account[i3]["UID"]
                    QuerySet3['Name'] = account[i3]["Name"]
                    break
                elif Transfer[i1]["ToAccountID"] == account[i3]["DisplayId"]:
                    QuerySet3['UID'] = account[i3]["UID"]
                    QuerySet3['Name'] = account[i3]["Name"]
                    break

            QuerySet1["ToAccount"] = QuerySet3
            QuerySet1["FromAccount"] = QuerySet2
            payload = json.dumps(QuerySet1)

            id_or_name_value_for_error = (
                Transfer[i1]["TransferNumber"]
                if Transfer[i1]["TransferNumber"] is not None
                else None
            )

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/Banking/TransferMoneyTxn"
            if Transfer[i1]['is_pushed'] == 0:
                asyncio.run(
                    post_data_in_myob(url, headers, payload, dbname['xero_bank_transfer'], _id, job_id, task_id,
                                      id_or_name_value_for_error))
            else:
                pass


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
