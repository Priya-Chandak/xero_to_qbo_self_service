import asyncio
import json
from datetime import datetime

from apps.home.data_util import get_job_details
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_spend_money_from_xero_to_myobledger(job_id, task_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        dbname = get_mongodb_database()

        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        spend_money = dbname['xero_spend_money'].find({'job_id': job_id})
        xero_spend_money = []
        for p1 in spend_money:
            xero_spend_money.append(p1)

        # m1=[]
        # for m in range(0,len(xero_spend_money)):
        #     # if multiple_invoice[m]['LineAmountTypes']=="Exclusive":
        #     if xero_spend_money[m]['BankTransactionID'] in ['ffc58587-2921-4050-a26c-f3c7f6a95925', 'b0ebd44e-9cb4-4a6c-9d74-2bcc3d4b6369', '82b0a340-18f6-4a62-9976-ea194a712d52']:
        #         m1.append(xero_spend_money[m])

        # xero_spend_money = m1

        myob_coa1 = dbname['chart_of_account'].find({'job_id': job_id})
        myob_coa = []
        for p2 in myob_coa1:
            myob_coa.append(p2)

        xero_coa1 = dbname['xero_coa'].find({'job_id': job_id})
        xero_coa = []
        for p3 in xero_coa1:
            xero_coa.append(p3)

        xero_archived_coa1 = dbname['xero_archived_coa'].find({"job_id":job_id})
        xero_archived_coa = []
        for k4 in range(0, dbname['xero_archived_coa'].count_documents({"job_id":job_id})):
            xero_archived_coa.append(xero_archived_coa1[k4])


        taxcode_myob1 = dbname['taxcode_myob'].find({'job_id': job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({'job_id': job_id})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({'job_id': job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        myob_supplier1 = dbname['supplier'].find({'job_id': job_id})
        myob_supplier = []
        for p6 in myob_supplier1:
            myob_supplier.append(p6)

        myob_customer1 = dbname['customer'].find({'job_id': job_id})
        myob_customer = []
        for p6 in myob_customer1:
            myob_customer.append(p6)

        myob_job1 = dbname['job'].find({'job_id': job_id})
        myob_job = []
        for p7 in myob_job1:
            myob_job.append(p7)

        xero_job1 = dbname['xero_job'].find({'job_id': job_id})
        xero_job = []
        for p8 in xero_job1:
            xero_job.append(p8)

        for i in range(0, len(xero_spend_money)):
            _id = xero_spend_money[i]['_id']
            task_id = xero_spend_money[i]['task_id']
            Queryset1 = {'Lines': []}
            account = {}
            contact = {}

            for i4 in range(0, len(myob_coa)):
                if myob_coa[i4]['IsHeader'] != True:
                    if xero_spend_money[i]['BankAccountName'].lower().strip() == myob_coa[i4]['Name'].lower().strip():
                        
                        account['UID'] = myob_coa[i4]['UID']
                        account['Name'] = myob_coa[i4]['Name']
                    elif xero_spend_money[i]['BankAccountName'][0:60] == myob_coa[i4]['Name']:
                        
                        account['UID'] = myob_coa[i4]['UID']
                        account['Name'] = myob_coa[i4]['Name']

            Queryset1['account'] = account

            for i3 in range(0, len(myob_supplier)):
                if xero_spend_money[i]['ContactName'][0:50] == myob_supplier[i3]['CompanyName']:
                    contact['UID'] = myob_supplier[i3]['UID']
                    contact['Name'] = myob_supplier[i3]['CompanyName']
                    contact['Type'] = 'Supplier'
                    continue
                elif 'CompanyName' in myob_supplier[i3] and myob_supplier[i3]['CompanyName']!= None:
                    if myob_supplier[i3]['CompanyName'].startswith(xero_spend_money[i]['ContactName']) and \
                        myob_supplier[i3]['CompanyName'].endswith("- S"):
                        contact['UID'] = myob_supplier[i3]['UID']
                        contact['Name'] = myob_supplier[i3]['CompanyName']
                        contact['Type'] = 'Supplier'
                        break


            for i31 in range(0, len(myob_customer)):
                if 'DisplayName' in myob_customer[i31]:
                    if xero_spend_money[i]['ContactName'][0:50] == myob_customer[i31]['DisplayName']:
                        contact['UID'] = myob_customer[i31]['UID']
                        contact['Name'] = myob_customer[i31]['DisplayName']
                        contact['Type'] = 'Customer'
                        continue
                        
                elif 'Company_Name' in myob_customer[i31] and myob_customer[i31]['Company_Name']!= None:
                    if myob_customer[i31]['Company_Name'].startswith(xero_spend_money[i]['ContactName']) and \
                            myob_customer[i31]['Company_Name'].endswith("- C"):
                        contact['UID'] = myob_customer[i31]['UID']
                        contact['Name'] = myob_customer[i31]['Company_Name']
                        contact['Type'] = 'Customer'
                        continue
                    elif myob_customer[i31]['Company_Name'].startswith(xero_spend_money[i]['ContactName']):
                        contact['UID'] = myob_customer[i31]['UID']
                        contact['Name'] = myob_customer[i31]['Company_Name']
                        contact['Type'] = 'Customer'
                        continue
                elif myob_customer[i31]['Company_Name'].strip().lower() == xero_spend_money[i][
                        'ContactName'][0:50].strip().lower():
                        contact['UID'] = myob_customer[i31]['UID']
                        contact['Name'] = myob_customer[i31]['Company_Name']
                        contact['Type'] = 'Customer'
                        break

            Queryset1['Contact'] = contact

            if xero_spend_money[i]['Reference'] != None:
                Queryset1['PaymentNumber'] = xero_spend_money[i]['Reference'][0:13]
            else:
                Queryset1['PaymentNumber'] = xero_spend_money[i]["BankTransactionID"][-12:]

            # Queryset1['StatementParticulars'] = Queryset1['PaymentNumber']
            Queryset1['PayFrom'] = "account"
            Queryset1['Date'] = xero_spend_money[i]['Date']
            Queryset1['AmountPaid'] = xero_spend_money[i]['TotalAmount']
            Queryset1['TotalTax'] = xero_spend_money[i]['TotalTax']

            for j in range(0, len(xero_spend_money[i]['Line'])):
                lineitem = {}
                lineaccount = {}
                taxcode = {}
                tracking = {}
                lineitem['Amount'] = xero_spend_money[i]['Line'][j]['LineAmount']
                if "Description" in xero_spend_money[i]['Line'][j]:
                    lineitem['Memo'] = xero_spend_money[i]['Line'][j]['Description']

                lineitem['UnitCount'] = xero_spend_money[i]['Line'][j]['Quantity']

        

                # for i2 in range(0, len(myob_coa)):
                #     if xero_spend_money[i]['Line'][j]['AccountCode'] == myob_coa[i2]['DisplayId']:
                #         lineaccount['UID'] = myob_coa[i2]['UID']
                #         break
                #     elif xero_spend_money[i]['Line'][j]['AccountCode'] == str(myob_coa[i2]['Number']):
                #         lineaccount['UID'] = myob_coa[i2]['UID']
                #         break
                #     else:
                #         for j6 in range(0, len(xero_coa)):
                #             if xero_spend_money[i]['Line'][j]['AccountCode'] == xero_coa[j6]["Code"]:
                #                 if xero_coa[j6]["Name"] == myob_coa[i2]["Name"]:
                #                     lineaccount['UID'] = myob_coa[i2]['UID']
                #                     break
                            
                #             elif xero_spend_money[i]['Line'][j]['AccountCode']  == myob_coa[i2]['DisplayId']:
                #                 lineaccount['UID'] = myob_coa[i2]['UID']
                #                 break

                #             # elif myob_coa[i2]['DisplayId'].endswith(xero_spend_money[i]['Line'][j]['AccountCode'].replace(".","")) :
                #             #     lineaccount['UID'] = myob_coa[i2]['UID']
                #             #     break
                #             # elif myob_coa[i2]['DisplayId'].endswith(xero_spend_money[i]['Line'][j]['AccountCode'].replace("/","")) :
                #             #     lineaccount['UID'] = myob_coa[i2]['UID']
                #             #     break

                # lineitem['account'] = lineaccount


                for i2 in range(0, len(myob_coa)):
                    for j6 in range(0, len(xero_coa)):

                        if myob_coa[i2]['IsHeader'] != True:
                            if xero_spend_money[i]['Line'][j]['AccountCode'] == xero_coa[j6]["Code"]:
                                if xero_coa[j6]["Name"] == myob_coa[i2]["Name"]:
                                    
                                    lineaccount['UID'] = myob_coa[i2]['UID']
                                    break
                        # elif myob_coa[i2]['DisplayId'].endswith(xero_receive_money[i]['Line'][j]['AccountCode'].replace(".","")) :
                        #     lineaccount['UID'] = myob_coa[i2]['UID']
                        #     break
                        # elif myob_coa[i2]['DisplayId'].endswith(xero_receive_money[i]['Line'][j]['AccountCode'].replace("/","")) :
                        #     lineaccount['UID'] = myob_coa[i2]['UID']
                        #     break

                            elif xero_spend_money[i]['Line'][j]['AccountCode'] == myob_coa[i2]['DisplayId']:
                                lineaccount['UID'] = myob_coa[i2]['UID']
                                break

                for n in range(0,len(xero_archived_coa)):    
                    for p1 in range(0,len(myob_coa)):

                        if myob_coa[p1]['IsHeader'] != True:
                            if xero_spend_money[i]['Line'][j]['AccountCode'] == xero_archived_coa[n]['Code']:
                                if xero_archived_coa[n]['Name'] == myob_coa[p1]["Name"]:
                                    lineaccount['UID'] = myob_coa[p1]["UID"]


                if lineaccount != {} and lineaccount != None:
                    lineitem['account'] = lineaccount
                    


                for i21 in range(0, len(myob_job)):
                    if 'TrackingName' in xero_spend_money[i]['Line'][j]:
                        if xero_spend_money[i]['Line'][j]['TrackingName'] == myob_job[i21]['Name']:
                            tracking['UID'] = myob_job[i21]['UID']
                            tracking['Name'] = myob_job[i21]['Name']
                            tracking['Number'] = myob_job[i21]['Number']

                if tracking != {} and tracking != None:
                    lineitem['Job'] = tracking
                else:
                    lineitem['Job'] = None

                for j3 in range(0, len(taxcode_myob)):
                    for j2 in range(0, len(xero_tax)):
                        if 'TaxType' in xero_spend_money[i]['Line'][j]:
                            if xero_spend_money[i]['Line'][j]["TaxType"] != None and xero_spend_money[i]['Line'][j][
                                "TaxType"] != 'NONE':
                                if xero_spend_money[i]['Line'][j]['TaxType'] == xero_tax[j2]['TaxType']:
                                    if xero_tax[j2]['TaxType'] in ['CAPEXINPUT', 'INPUT', 'OUTPUT', "INPUT2",
                                                                   "OUTPUT2"]:
                                        if taxcode_myob[j3]['Code'] == 'GST' or taxcode_myob1[j3]['Code'] == 'S15':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']

                                    elif xero_tax[j2]['TaxType'] in ['EXEMPTCAPITAL', 'EXEMPTEXPENSES', 'EXEMPTEXPORT',
                                                                     'EXEMPTOUTPUT','TAX005']:
                                        if taxcode_myob[j3]['Code'] == 'FRE':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']

                                    elif xero_tax[j2]['TaxType'] in ["INPUTTAXED"]:
                                        if taxcode_myob[j3]['Code'] == 'INP':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']

                                    elif xero_tax[j2]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2", "NONE"]:
                                        if taxcode_myob[j3]['Code'] == 'N-T':
                                            taxcode['UID'] = taxcode_myob[j3]['UID']

                            elif xero_spend_money[i]['Line'][j]['TaxType'] in ['NONE', None]:
                                if taxcode_myob[j3]['Code'] == 'N-T':
                                    taxcode['UID'] = taxcode_myob[j3]['UID']

                lineitem['TaxCode'] = taxcode

                if xero_spend_money[i]['LineAmountTypes'] == 'Inclusive':
                    Queryset1['IsTaxInclusive'] = True
                else:
                    Queryset1['IsTaxInclusive'] = False

                Queryset1['Lines'].append(lineitem)

            payload = json.dumps(Queryset1)
            
            id_or_name_value_for_error = str(xero_spend_money[i]['Date'])+"-"+str(xero_spend_money[i]['ContactName'])+"-"+str(xero_spend_money[i]['TotalAmount'])
            
            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/Banking/SpendMoneyTxn"
            if xero_spend_money[i]['is_pushed']==0:
                asyncio.run(
                    post_data_in_myob(url, headers, payload, dbname['xero_spend_money'], _id, job_id, task_id,
                                    id_or_name_value_for_error))
            else:
                pass


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
