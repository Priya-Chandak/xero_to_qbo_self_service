import asyncio
import json
from datetime import datetime

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_journal_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        journal1 = dbname['xero_manual_journal'].find({"job_id": job_id})

        journal = []
        for p1 in journal1:
            journal.append(p1)

        chart_of_account1 = dbname['chart_of_account'].find({"job_id": job_id})
        chart_of_account = []
        for k3 in range(0, dbname['chart_of_account'].count_documents({"job_id": job_id})):
            chart_of_account.append(chart_of_account1[k3])

        xero_coa1 = dbname['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for k3 in range(0, dbname['xero_coa'].count_documents({"job_id": job_id})):
            xero_coa.append(xero_coa1[k3])

        taxcode_myob1 = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({"job_id": job_id})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        job11 = dbname['job'].find({"job_id": job_id})
        job = []
        for k8 in range(0, dbname['job'].count_documents({"job_id": job_id})):
            job.append(job11[k8])

        journal=journal
        for i in range(0, len(journal)):
            print(journal[i])
            _id = journal[i]['_id']
            task_id = journal[i]['task_id']
            QuerySet1 = {"Lines": []}
            QuerySet1["DisplayID"] = journal[i]["Narration"][0:12]
            QuerySet1["JournalType"] = "General"
            journal_date = journal[i]["Date"]
            journal_date11 = int(journal_date[6:16])
            journal_date12 = datetime.utcfromtimestamp(journal_date11).strftime('%Y-%m-%d')
            QuerySet1["DateOccurred"] = journal_date12

            QuerySet1["Memo"] = journal[i]["Narration"]

            for j in range(0, len(journal[i]["Line"])):
                QuerySet2 = {}
                QuerySet3 = {}
                account = {}
                line_job = {}
                taxcode = {}

                if journal[i]["Line"][j]["LineAmount"] < 0:
                    for j1 in range(0, len(chart_of_account)):
                        for j2 in range(0, len(xero_coa)):
                            if journal[i]["Line"][j]["AccountCode"] == xero_coa[j2]["Code"]:
                                if xero_coa[j2]["Name"] == chart_of_account[j1]['Name']:
                                    account['UID'] = chart_of_account[j1]["UID"]
                                    break
                            
                            # elif journal[i]["Line"][j]["AccountCode"] == str(chart_of_account[j1]["DisplayId"]):

                            #     account['UID'] = chart_of_account[j1]["UID"]
                            #     break

                    QuerySet2['Account'] = account

                    # for j3 in range(0,len(job)):
                    #     if journal[i]["Line"][j]["ClassRef"]["name"]== job[j3]["Name"]:
                    #         job['UID'] =job[j3]["UID"]

                    # for j3 in range(0,len(job)):
                    #     if 'ClassRef' in journal[i]["Line"][j]:
                    #         if job[j3]['Name'] == journal[i]["Line"][j]["ClassRef"]["name"]:
                    #             line_job['UID']=job[j3]['UID']

                    #         elif (job[j3]['Name']).startswith(journal[i]["Line"][j]["ClassRef"]["name"].split("-")[0]):
                    #             line_job['UID']=job[j3]['UID']

                    # if line_job=={}:
                    #     QuerySet2['Job']=None  
                    # else:
                    #     QuerySet2['Job']=line_job

                    QuerySet2["IsCredit"] = True

                    for j3 in range(0, len(taxcode_myob)):
                        for k1 in range(0, len(xero_tax)):
                            if 'TaxType' in journal[i]["Line"][j]:
                                if journal[i]["Line"][j]["TaxType"] == xero_tax[k1]['TaxType']:
                                    
                                    
                                    if xero_tax[k1]['TaxType'] in ['CAPEXINPUT', 'OUTPUT', 'INPUT','INPUT2','INPUT1']:
                                       
                                        if taxcode_myob[j3]['Code'] == 'GST' or taxcode_myob1[j3]['Code'] == 'S15':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']
                                            taxrate1 = taxcode_myob[j3]['Rate']
                                            break
                                    elif xero_tax[k1]['TaxType'] in ["EXEMPTCAPITAL", 'EXEMPTEXPENSES', 'EXEMPTOUTPUT',
                                                                     'EXEMPTEXPORT']:
                                        
                                        if taxcode_myob[j3]['Code'] == 'FRE':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']
                                            taxrate1 = taxcode_myob[j3]['Rate']
                                            break
                                    elif xero_tax[k1]['TaxType'] in ["INPUTTAXED"]:
                                        
                                        if taxcode_myob[j3]['Code'] == 'INP':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']
                                            taxrate1 = taxcode_myob[j3]['Rate']
                                            break
                                    elif xero_tax[k1]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2","NONE", None]:
                                        
                                        if taxcode_myob[j3]['Code'] == 'N-T':
                                            
                                            taxcode['UID'] = taxcode_myob[j3]['UID']
                                            taxrate1 = taxcode_myob[j3]['Rate']
                                            break


                    QuerySet2['TaxCode'] = taxcode

                    if journal[i]['LineAmountTypes'] == 'Inclusive':
                        QuerySet1['IsTaxInclusive'] = True
                    else:
                        QuerySet1['IsTaxInclusive'] = False

                    QuerySet2["Amount"] = abs(journal[i]["Line"][j]["LineAmount"])

                    if 'Description' in journal[i]["Line"][j]:
                        QuerySet2["Memo"] = journal[i]["Line"][j]["Description"]

                    QuerySet1['Lines'].append(QuerySet2)

                else:
                    QuerySet3 = {}
                    account = {}
                    line_job = {}
                    taxcode = {}
                    for j1 in range(0, len(chart_of_account)):
                        for j2 in range(0, len(xero_coa)):
                            if journal[i]["Line"][j]["AccountCode"] == xero_coa[j2]["Code"]:
                                if xero_coa[j2]["Name"] == chart_of_account[j1]['Name']:
                                    account['UID'] = chart_of_account[j1]["UID"]
                    QuerySet3['Account'] = account

                    # for j3 in range(0,len(job)):
                    #     if journal[i]["Line"][j]["ClassRef"]["name"]== job[j3]["Name"]:
                    #         job['UID'] =job[j3]["UID"]

                    # for j3 in range(0,len(job)):
                    #     if 'ClassRef' in journal[i]["Line"][j]:
                    #         if job[j3]['Name'] == journal[i]["Line"][j]["ClassRef"]["name"]:
                    #             line_job['UID']=job[j3]['UID']

                    #         elif (job[j3]['Name']).startswith(journal[i]["Line"][j]["ClassRef"]["name"].split("-")[0]):
                    #             line_job['UID']=job[j3]['UID']

                    # if line_job=={}:
                    #     QuerySet3['Job']=None  
                    # else:
                    #     QuerySet3['Job']=line_job

                    QuerySet3["IsCredit"] = False

                    for j7 in range(0, len(taxcode_myob)):
                        for k4 in range(0, len(xero_tax)):
                            if 'TaxType' in journal[i]["Line"][j]:
                                if journal[i]["Line"][j]["TaxType"] == xero_tax[k4]['TaxType']:
                                    
                                    if xero_tax[k4]['TaxType'] in ['CAPEXINPUT', 'OUTPUT', 'INPUT',"INPUT2","INPUT1"]:

                                        if taxcode_myob[j7]['Code'] == 'GST' or taxcode_myob1[j7]['Code'] == 'S15':
                                            taxcode['UID'] = taxcode_myob[j7]['UID']
                                            break
                                    elif xero_tax[k4]['TaxType'] in ["EXEMPTCAPITAL", 'EXEMPTEXPENSES', 'EXEMPTOUTPUT',
                                                                     'EXEMPTEXPORT']:
                                        
                                        if taxcode_myob[j7]['Code'] == 'FRE':
                                            taxcode['UID'] = taxcode_myob[j7]['UID']
                                            break
                                    elif xero_tax[k4]['TaxType'] in ["INPUTTAXED"]:
                                        
                                        if taxcode_myob[j7]['Code'] == 'INP':
                                            taxcode['UID'] = taxcode_myob[j7]['UID']
                                            break
                                    elif xero_tax[k4]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2","NONE", None]:
                                        
                                        if taxcode_myob[j7]['Code'] == 'N-T':
                                            taxcode['UID'] = taxcode_myob[j7]['UID']
                                            break
                                
                     
                    QuerySet3['TaxCode'] = taxcode

                    if journal[i]['LineAmountTypes'] == 'Inclusive':
                        QuerySet1['IsTaxInclusive'] = True
                    else:
                        QuerySet1['IsTaxInclusive'] = False

                    QuerySet3["Amount"] = abs(journal[i]["Line"][j]["LineAmount"])

                    if 'Description' in journal[i]["Line"][j]:
                        QuerySet3["Memo"] = journal[i]["Line"][j]["Description"]
                    QuerySet1['Lines'].append(QuerySet3)

            payload = json.dumps(QuerySet1)
            print(payload)
            id_or_name_value_for_error = (
                journal[i]["ManualJournalID"]
                if journal[i]["ManualJournalID"] is not None
                else "")

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/GeneralLedger/GeneralJournal"
            if journal[i]['is_pushed']==0:
                asyncio.run(
                    post_data_in_myob(url, headers, payload, dbname['xero_manual_journal'], _id, job_id, task_id,
                                    id_or_name_value_for_error))
            else:
                pass



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
