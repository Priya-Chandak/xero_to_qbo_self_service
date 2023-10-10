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

        taxcode_myob1 = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({})):
            taxcode_myob.append(taxcode_myob1[k7])

        Transfer = []
        for k in xero_bank_transfer1.find({'job_id': job_id}):
            Transfer.append(k)

        account = []
        for p in chart_of_account1.find({'job_id': job_id}):
            account.append(p)
        chart_of_account = account
        journal = Transfer
        for i1 in range(0, len(journal)):
            _id = Transfer[i1]['_id']
            task_id = Transfer[i1]['task_id']
            QuerySet1 = {"Lines": []}
            QuerySet1["DisplayID"] = journal[i1]["TransferNumber"][-5:]
            QuerySet1["JournalType"] = "General"
            journal_date = journal[i1]["Date"][0:10]
            QuerySet1["DateOccurred"] = journal_date
            if "PrivateNote" in journal[i1]:
                QuerySet1["Memo"] = journal[i1]["Memo"]

            for j1 in range(0, len(chart_of_account)):
                QuerySet2 = {}
                QuerySet3 = {}
                account = {}
                line_job = {}
                taxcode = {}
                if journal[i1]["FromAccountRef"]["name"] == chart_of_account[j1]["Name"]:
                    account['UID'] = chart_of_account[j1]["UID"]

                    QuerySet2['account'] = account

                    if chart_of_account[j1]["Account_Type"] == "Bank":
                        QuerySet2["IsCredit"] = True
                        QuerySet2["Amount"] = journal[i1]["Amount"]

                    else:
                        QuerySet2["IsCredit"] = False
                        QuerySet2["Amount"] = journal[i1]["Amount"]

                    for j3 in range(0, len(taxcode_myob)):

                        if taxcode_myob[j3]['Code'] == 'N-T':
                            taxcode['UID'] = taxcode_myob[j3]['UID']

                    QuerySet2['TaxCode'] = taxcode

                    QuerySet1['Lines'].append(QuerySet2)

                if journal[i1]["ToAccountRef"]["name"] == chart_of_account[j1]["Name"]:
                    account['UID'] = chart_of_account[j1]["UID"]
                    QuerySet3['account'] = account

                    if chart_of_account[j1]["Account_Type"] == "Bank":
                        QuerySet3["IsCredit"] = True
                        QuerySet3["Amount"] = journal[i1]["Amount"]

                    else:
                        QuerySet3["IsCredit"] = False
                        QuerySet3["Amount"] = journal[i1]["Amount"]

                    for j3 in range(0, len(taxcode_myob)):

                        if taxcode_myob[j3]['Code'] == 'N-T':
                            taxcode['UID'] = taxcode_myob[j3]['UID']

                    QuerySet3['TaxCode'] = taxcode

                    QuerySet1['Lines'].append(QuerySet3)
            payload = json.dumps(QuerySet1)
            print(payload)

            id_or_name_value_for_error = (
                journal[i1]["TransferNumber"]
                if journal[i1]["TransferNumber"] is not None
                else None
            )

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/GeneralLedger/GeneralJournal"
            asyncio.run(
                post_data_in_myob(url, headers, payload, dbname['xero_bank_transfer'], _id, job_id, task_id,
                                  id_or_name_value_for_error))



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
