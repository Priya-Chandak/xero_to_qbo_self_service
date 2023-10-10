import json

from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_invoice_as_journal_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)

        url = f"{base_url}/GeneralLedger/GeneralJournal"

        invoice1 = dbname['xero_invoice'].find({"job_id": job_id})

        invoice = []
        for p1 in invoice1:
            invoice.append(p1)

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

        invoice = invoice

        for i in range(0, len(invoice)):
            _id = invoice[i]['_id']
            task_id = invoice[i]['task_id']
            QuerySet1 = {"Lines": []}
            QuerySet1["DisplayID"] = invoice[i]["Inv_No"]
            QuerySet1["JournalType"] = "General"
            invoice_date = invoice[i]["TxnDate"]
            # invoice_date11 = int(invoice_date[6:16])
            # invoice_date12 = datetime.utcfromtimestamp(invoice_date11).strftime('%Y-%m-%d')
            QuerySet1["DateOccurred"] = invoice_date

            QuerySet1["Memo"] = invoice[i]["Inv_No"]

            for j in range(0, len(invoice[i]["Line"])):
                QuerySet2 = {}
                QuerySet3 = {}
                debit_account = {}
                credit_account = {}
                line_job = {}
                taxcode = {}

                for j1 in range(0, len(chart_of_account)):
                    for j2 in range(0, len(xero_coa)):
                        if invoice[i]["Line"][j]["AccountCode"] == xero_coa[j2]["Code"]:
                            if xero_coa[j2]["Name"] == chart_of_account[j1]['Name']:
                                debit_account['UID'] = chart_of_account[j1]["UID"]
                                QuerySet3['account'] = debit_account
                        if chart_of_account[j1]['Name'] == 'Accounts Receivable':
                            credit_account['UID'] = chart_of_account[j1]["UID"]
                            QuerySet2['account'] = credit_account

                QuerySet2["IsCredit"] = False
                QuerySet3["IsCredit"] = True

                for j3 in range(0, len(taxcode_myob)):
                    for k1 in range(0, len(xero_tax)):
                        if 'TaxType' in invoice[i]["Line"][j]:
                            if invoice[i]["Line"][j]["TaxType"] == xero_tax[k1]['TaxType']:
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

                if invoice[i]['LineAmountTypes'] == 'Inclusive':
                    QuerySet1['IsTaxInclusive'] = False
                    QuerySet2["Amount"] = abs(invoice[i]["TotalAmount"] - invoice[i]["TotalTax"])
                    QuerySet3["Amount"] = abs(invoice[i]["TotalAmount"] - invoice[i]["TotalTax"])

                else:
                    QuerySet2["Amount"] = abs(invoice[i]['TotalAmount'])
                    QuerySet3["Amount"] = abs(invoice[i]['TotalAmount'])

                QuerySet2["Memo"] = invoice[i]["Line"][j]["Description"]
                QuerySet3["Memo"] = invoice[i]["Line"][j]["Description"]

                QuerySet1['Lines'].append(QuerySet2)
                QuerySet1['Lines'].append(QuerySet3)

                # for j3 in range(0,len(job)):
                #     if invoice[i]["Line"][j]["ClassRef"]["name"]== job[j3]["Name"]:
                #         job['UID'] =job[j3]["UID"]

                # for j3 in range(0,len(job)):
                #     if 'ClassRef' in invoice[i]["Line"][j]:
                #         if job[j3]['Name'] == invoice[i]["Line"][j]["ClassRef"]["name"]:
                #             line_job['UID']=job[j3]['UID']

                #         elif (job[j3]['Name']).startswith(invoice[i]["Line"][j]["ClassRef"]["name"].split("-")[0]):
                #             line_job['UID']=job[j3]['UID']

                # if line_job=={}:
                #     QuerySet2['Job']=None
                # else:
                #     QuerySet2['Job']=line_job

            payload = json.dumps(QuerySet1)

            id_or_name_value_for_error = (
                invoice[i]["Inv_No"]
                if invoice[i]["Inv_No"] is not None
                else "")

            post_data_in_myob(
                url, headers, payload, invoice1, _id, job_id, task_id, id_or_name_value_for_error
            )



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)


def add_xero_creditnote_as_journal_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)

        url = f"{base_url}/GeneralLedger/GeneralJournal"

        invoice1 = dbname['xero_creditnote'].find({"job_id": job_id})

        invoice = []
        for p1 in invoice1:
            invoice.append(p1)

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

        invoice = invoice

        for i in range(0, len(invoice)):
            _id = invoice[i]['_id']
            task_id = invoice[i]['task_id']
            QuerySet1 = {"Lines": [], "DisplayID": invoice[i]["Inv_No"], "JournalType": "General"}
            invoice_date = invoice[i]["TxnDate"]
            # invoice_date11 = int(invoice_date[6:16])
            # invoice_date12 = datetime.utcfromtimestamp(invoice_date11).strftime('%Y-%m-%d')
            QuerySet1["DateOccurred"] = invoice_date

            # QuerySet1["Memo"]=invoice[i]["Inv_No"]

            for j in range(0, len(invoice[i]["Line"])):
                QuerySet2 = {}
                QuerySet3 = {}
                debit_account = {}
                credit_account = {}
                line_job = {}
                taxcode = {}

                for j1 in range(0, len(chart_of_account)):
                    for j2 in range(0, len(xero_coa)):
                        if invoice[i]["Line"][j]["AccountCode"] == xero_coa[j2]["Code"]:
                            if xero_coa[j2]["Name"] == chart_of_account[j1]['Name']:
                                debit_account['UID'] = chart_of_account[j1]["UID"]
                                QuerySet3['account'] = debit_account
                        if chart_of_account[j1]['Name'] == 'Accounts Receivable':
                            credit_account['UID'] = chart_of_account[j1]["UID"]
                            QuerySet2['account'] = credit_account

                QuerySet2["IsCredit"] = True
                QuerySet3["IsCredit"] = False

                for j3 in range(0, len(taxcode_myob)):
                    for k1 in range(0, len(xero_tax)):
                        if 'TaxType' in invoice[i]["Line"][j]:
                            if invoice[i]["Line"][j]["TaxType"] == xero_tax[k1]['TaxType']:
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

                if invoice[i]['LineAmountTypes'] == 'Inclusive':
                    QuerySet1['IsTaxInclusive'] = False
                    QuerySet2["Amount"] = abs(invoice[i]["TotalAmount"] - invoice[i]["TotalTax"])
                    QuerySet3["Amount"] = abs(invoice[i]["TotalAmount"] - invoice[i]["TotalTax"])

                else:
                    QuerySet2["Amount"] = abs(invoice[i]['TotalAmount'])
                    QuerySet3["Amount"] = abs(invoice[i]['TotalAmount'])

                QuerySet2["Memo"] = invoice[i]["Line"][j]["Description"]
                QuerySet3["Memo"] = invoice[i]["Line"][j]["Description"]

                QuerySet1['Lines'].append(QuerySet3)
                QuerySet1['Lines'].append(QuerySet2)

                # for j3 in range(0,len(job)):
                #     if invoice[i]["Line"][j]["ClassRef"]["name"]== job[j3]["Name"]:
                #         job['UID'] =job[j3]["UID"]

                # for j3 in range(0,len(job)):
                #     if 'ClassRef' in invoice[i]["Line"][j]:
                #         if job[j3]['Name'] == invoice[i]["Line"][j]["ClassRef"]["name"]:
                #             line_job['UID']=job[j3]['UID']

                #         elif (job[j3]['Name']).startswith(invoice[i]["Line"][j]["ClassRef"]["name"].split("-")[0]):
                #             line_job['UID']=job[j3]['UID']

                # if line_job=={}:
                #     QuerySet2['Job']=None
                # else:
                #     QuerySet2['Job']=line_job

            payload = json.dumps(QuerySet1)
            id_or_name_value_for_error = (
                invoice[i]["Inv_No"]
                if invoice[i]["Inv_No"] is not None
                else "")

            post_data_in_myob(
                url, headers, payload, invoice1, _id, job_id, task_id, id_or_name_value_for_error
            )



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
