import json

from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_bill_as_journal_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)

        url = f"{base_url}/GeneralLedger/GeneralJournal"

        bill1 = dbname['xero_bill'].find({"job_id": job_id})

        bill = []
        for p1 in bill1:
            bill.append(p1)

        chart_of_account1 = dbname['chart_of_account'].find({"job_id": job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({})):
            chart_of_account.append(chart_of_account1[k3])

        xero_coa1 = dbname['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for k3 in range(0, dbname['xero_coa'].count_documents({})):
            xero_coa.append(xero_coa1[k3])

        taxcode_myob1 = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        job11 = dbname['job'].find({"job_id": job_id})
        job = []
        for k8 in range(0, dbname['job'].count_documents({})):
            job.append(job11[k8])

        for i in range(0, len(bill)):
            _id = bill[i]['_id']
            task_id = bill[i]['task_id']
            QuerySet1 = {"Lines": []}
            QuerySet1["DisplayID"] = bill[i]["Inv_No"]
            QuerySet1["JournalType"] = "General"
            bill_date = bill[i]["TxnDate"]
            # bill_date11 = int(bill_date[6:16])
            # bill_date12 = datetime.utcfromtimestamp(bill_date11).strftime('%Y-%m-%d')
            QuerySet1["DateOccurred"] = bill_date

            # QuerySet1["Memo"]=bill[i]["Inv_No"]

            for j in range(0, len(bill[i]["Line"])):
                QuerySet2 = {}
                QuerySet3 = {}
                debit_account = {}
                credit_account = {}
                line_job = {}
                taxcode = {}

                for j1 in range(0, len(chart_of_account)):
                    for j2 in range(0, len(xero_coa)):
                        if bill[i]["Line"][j]["AccountCode"] == xero_coa[j2]["Code"]:
                            if xero_coa[j2]["Name"] == chart_of_account[j1]['Name']:
                                debit_account['UID'] = chart_of_account[j1]["UID"]
                                QuerySet3['account'] = debit_account
                        if chart_of_account[j1]['Name'] == 'Accounts Payable':
                            credit_account['UID'] = chart_of_account[j1]["UID"]
                            QuerySet2['account'] = credit_account

                QuerySet2["IsCredit"] = True
                QuerySet3["IsCredit"] = False

                for j3 in range(0, len(taxcode_myob)):
                    for k1 in range(0, len(xero_tax)):
                        if 'TaxType' in bill[i]["Line"][j]:
                            if bill[i]["Line"][j]["TaxType"] == xero_tax[k1]['TaxType']:
                                if xero_tax[k1]['TaxType'] in ['CAPEXINPUT', 'OUTPUT', 'INPUT']:
                                    if taxcode_myob[j3]['Code'] == 'GST':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[k1]['TaxType'] in ["EXEMPTCAPITAL", 'EXEMPTEXPENSES', 'EXEMPTOUTPUT',
                                                                 'EXEMPTEXPORT']:
                                    if taxcode_myob[j3]['Code'] == 'FRE':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[k1]['TaxType'] in ["INPUTTAXED"]:
                                    if taxcode_myob[j3]['Code'] == 'INP':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[k1]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2"]:
                                    if taxcode_myob[j3]['Code'] == 'N-T':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']

                QuerySet2['TaxCode'] = taxcode
                QuerySet3['TaxCode'] = taxcode

                if bill[i]['LineAmountTypes'] == 'Inclusive':
                    QuerySet1['IsTaxInclusive'] = False
                    QuerySet2["Amount"] = abs(bill[i]["TotalAmount"] - bill[i]["TotalTax"])
                    QuerySet3["Amount"] = abs(bill[i]["TotalAmount"] - bill[i]["TotalTax"])

                else:
                    QuerySet2["Amount"] = abs(bill[i]['TotalAmount'])
                    QuerySet3["Amount"] = abs(bill[i]['TotalAmount'])

                QuerySet2["Memo"] = bill[i]["Line"][j]["Description"]
                QuerySet3["Memo"] = bill[i]["Line"][j]["Description"]

                QuerySet1['Lines'].append(QuerySet3)
                QuerySet1['Lines'].append(QuerySet2)

                # for j3 in range(0,len(job)):
                #     if bill[i]["Line"][j]["ClassRef"]["name"]== job[j3]["Name"]:
                #         job['UID'] =job[j3]["UID"]

                # for j3 in range(0,len(job)):
                #     if 'ClassRef' in bill[i]["Line"][j]:
                #         if job[j3]['Name'] == bill[i]["Line"][j]["ClassRef"]["name"]:
                #             line_job['UID']=job[j3]['UID']

                #         elif (job[j3]['Name']).startswith(bill[i]["Line"][j]["ClassRef"]["name"].split("-")[0]):
                #             line_job['UID']=job[j3]['UID']

                # if line_job=={}:
                #     QuerySet2['Job']=None
                # else:
                #     QuerySet2['Job']=line_job

            payload = json.dumps(QuerySet1)
            print(payload)

            post_data_in_myob(
                url, headers, payload, bill1, _id, job_id, task_id, bill[i]["Inv_No"]
            )



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)


def add_xero_vendorcredit_as_journal_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)

        url = f"{base_url}/GeneralLedger/GeneralJournal"

        bill1 = dbname['xero_vendorcredit'].find({"job_id": job_id})

        bill = []
        for p1 in bill1:
            bill.append(p1)

        chart_of_account1 = dbname['chart_of_account'].find({"job_id": job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({})):
            chart_of_account.append(chart_of_account1[k3])

        xero_coa1 = dbname['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for k3 in range(0, dbname['xero_coa'].count_documents({})):
            xero_coa.append(xero_coa1[k3])

        taxcode_myob1 = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        job11 = dbname['job'].find({"job_id": job_id})
        job = []
        for k8 in range(0, dbname['job'].count_documents({})):
            job.append(job11[k8])

        bill = bill

        for i in range(0, len(bill)):
            _id = bill[i]['_id']
            task_id = bill[i]['task_id']
            QuerySet1 = {"Lines": []}
            QuerySet1["DisplayID"] = bill[i]["Inv_No"]
            QuerySet1["JournalType"] = "General"
            bill_date = bill[i]["TxnDate"]
            # bill_date11 = int(bill_date[6:16])
            # bill_date12 = datetime.utcfromtimestamp(bill_date11).strftime('%Y-%m-%d')
            QuerySet1["DateOccurred"] = bill_date

            # QuerySet1["Memo"]=bill[i]["Inv_No"]

            for j in range(0, len(bill[i]["Line"])):

                QuerySet2 = {}
                QuerySet3 = {}
                debit_account = {}
                credit_account = {}
                line_job = {}
                taxcode = {}

                for j1 in range(0, len(chart_of_account)):
                    for j2 in range(0, len(xero_coa)):
                        if bill[i]["Line"][j]["AccountCode"] == xero_coa[j2]["Code"]:
                            if xero_coa[j2]["Name"] == chart_of_account[j1]['Name']:
                                debit_account['UID'] = chart_of_account[j1]["UID"]
                                QuerySet3['account'] = debit_account
                        if chart_of_account[j1]['Name'] == 'Accounts Payable':
                            credit_account['UID'] = chart_of_account[j1]["UID"]
                            QuerySet2['account'] = credit_account

                QuerySet2["IsCredit"] = False
                QuerySet3["IsCredit"] = True

                for j3 in range(0, len(taxcode_myob)):
                    for k1 in range(0, len(xero_tax)):
                        if 'TaxType' in bill[i]["Line"][j]:
                            if bill[i]["Line"][j]["TaxType"] == xero_tax[k1]['TaxType']:
                                if xero_tax[k1]['TaxType'] in ['CAPEXINPUT', 'OUTPUT', 'INPUT']:
                                    if taxcode_myob[j3]['Code'] == 'GST':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[k1]['TaxType'] in ["EXEMPTCAPITAL", 'EXEMPTEXPENSES', 'EXEMPTOUTPUT',
                                                                 'EXEMPTEXPORT']:
                                    if taxcode_myob[j3]['Code'] == 'FRE':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[k1]['TaxType'] in ["INPUTTAXED"]:
                                    if taxcode_myob[j3]['Code'] == 'INP':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']
                                elif xero_tax[k1]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2"]:
                                    if taxcode_myob[j3]['Code'] == 'N-T':
                                        taxcode['UID'] = taxcode_myob[j3]['UID']
                                        taxrate1 = taxcode_myob[j3]['Rate']

                QuerySet2['TaxCode'] = taxcode
                QuerySet3['TaxCode'] = taxcode

                if bill[i]['LineAmountTypes'] == 'Inclusive':
                    QuerySet1['IsTaxInclusive'] = False
                    QuerySet2["Amount"] = abs(bill[i]["TotalAmount"] - bill[i]["TotalTax"])
                    QuerySet3["Amount"] = abs(bill[i]["TotalAmount"] - bill[i]["TotalTax"])

                else:
                    QuerySet2["Amount"] = abs(bill[i]['TotalAmount'])
                    QuerySet3["Amount"] = abs(bill[i]['TotalAmount'])

                QuerySet2["Memo"] = bill[i]["Line"][j]["Description"]
                QuerySet3["Memo"] = bill[i]["Line"][j]["Description"]

                QuerySet1['Lines'].append(QuerySet2)
                QuerySet1['Lines'].append(QuerySet3)

                # for j3 in range(0,len(job)):
                #     if bill[i]["Line"][j]["ClassRef"]["name"]== job[j3]["Name"]:
                #         job['UID'] =job[j3]["UID"]

                # for j3 in range(0,len(job)):
                #     if 'ClassRef' in bill[i]["Line"][j]:
                #         if job[j3]['Name'] == bill[i]["Line"][j]["ClassRef"]["name"]:
                #             line_job['UID']=job[j3]['UID']

                #         elif (job[j3]['Name']).startswith(bill[i]["Line"][j]["ClassRef"]["name"].split("-")[0]):
                #             line_job['UID']=job[j3]['UID']

                # if line_job=={}:
                #     QuerySet2['Job']=None
                # else:
                #     QuerySet2['Job']=line_job

            payload = json.dumps(QuerySet1)
            print(payload)

            post_data_in_myob(
                url, headers, payload, bill1, _id, job_id, task_id, bill[i]["Inv_No"]
            )




    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
