import asyncio
import json

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_spend_overpayment_as_spend_money(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        spend_money_data = dbname['xero_spend_overpayment']
        spend_money = dbname['xero_spend_overpayment'].find({"job_id": job_id})
        xero_spend_overpayment = []
        for p1 in spend_money:
            xero_spend_overpayment.append(p1)

        myob_coa1 = dbname['chart_of_account'].find({"job_id": job_id})
        myob_coa = []
        for p2 in myob_coa1:
            myob_coa.append(p2)

        xero_coa1 = dbname['xero_coa'].find({"job_id": job_id})
        xero_coa = []
        for p3 in xero_coa1:
            xero_coa.append(p3)

        taxcode_myob1 = dbname['taxcode_myob'].find({"job_id": job_id})
        taxcode_myob = []
        for k7 in range(0, dbname['taxcode_myob'].count_documents({"job_id": job_id})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

        myob_supplier1 = dbname['supplier'].find({"job_id": job_id})
        myob_supplier = []
        for p6 in myob_supplier1:
            myob_supplier.append(p6)

        myob_customer1 = dbname['customer'].find({"job_id": job_id})
        myob_customer = []
        for p6 in myob_customer1:
            myob_customer.append(p6)

        myob_job1 = dbname['job'].find({"job_id": job_id})
        myob_job = []
        for p7 in myob_job1:
            myob_job.append(p7)

        xero_job1 = dbname['xero_job'].find({"job_id": job_id})
        xero_job = []
        for p8 in xero_job1:
            xero_job.append(p8)

        for i in range(0, len(xero_spend_overpayment)):
            _id = xero_spend_overpayment[i]['_id']
            task_id = xero_spend_overpayment[i]['task_id']
            Queryset1 = {'Lines': []}
            account = {}
            contact = {}

            for i1 in range(0, len(xero_coa)):
                for i2 in range(0, len(myob_coa)):
                    if xero_spend_overpayment[i]['BankAccountName'] == xero_coa[i1]['Name']:
                        if xero_coa[i1]['Name'] == myob_coa[i2]['Name']:
                            account['UID'] = myob_coa[i2]['UID']
                            account['Name'] = myob_coa[i2]['Name']

            Queryset1['Account'] = account

            for i3 in range(0, len(myob_supplier)):
                if xero_spend_overpayment[i]['ContactName'] == myob_supplier[i3]['CompanyName']:
                    contact['UID'] = myob_supplier[i3]['UID']
                    contact['Name'] = myob_supplier[i3]['CompanyName']
                    contact['Type'] = 'Supplier'

            for i31 in range(0, len(myob_customer)):
                if 'DisplayName' in myob_customer[i31]:
                    if xero_spend_overpayment[i]['ContactName'] == myob_customer[i31]['DisplayName']:
                        contact['UID'] = myob_customer[i31]['UID']
                        contact['Name'] = myob_customer[i31]['DisplayName']
                        contact['Type'] = 'Customer'

                elif 'FirstName' in myob_customer[i31]:
                    if myob_customer[i31]['FirstName'].startswith(xero_spend_overpayment[i]['ContactName']) and \
                            myob_customer[i31]['FirstName'].endswith("- C"):
                        contact['UID'] = myob_customer[i31]['UID']
                        contact['Name'] = myob_customer[i31]['DisplayName']
                        contact['Type'] = 'Customer'

            Queryset1['Contact'] = contact

            Queryset1['PaymentNumber'] = xero_spend_overpayment[i]['Reference']
            Queryset1['PayFrom'] = "Account"
            Queryset1['Date'] = xero_spend_overpayment[i]['Date']
            Queryset1['AmountPaid'] = xero_spend_overpayment[i]['TotalAmount']
            Queryset1['TotalTax'] = xero_spend_overpayment[i]['TotalTax']

            for j in range(0, len(xero_spend_overpayment[i]['Line'])):
                lineitem = {}
                lineaccount = {}
                taxcode = {}
                tracking = {}
                lineitem['Amount'] = xero_spend_overpayment[i]['Line'][j]['LineAmount']
                lineitem['Memo'] = xero_spend_overpayment[i]['Line'][j]['Description']
                Queryset1['Memo'] = xero_spend_overpayment[i]['Line'][j]['Description']
                lineitem['UnitCount'] = xero_spend_overpayment[i]['Line'][j]['Quantity']

                for i2 in range(0, len(myob_coa)):
                    for i1 in range(0, len(xero_coa)):
                        if xero_spend_overpayment[i]['Line'][j]['AccountCode'] == xero_coa[i1]['Code']:
                            if xero_coa[i1]['Name'] == myob_coa[i2]['Name']:
                                lineaccount['UID'] = myob_coa[i2]['UID']

                lineitem['Account'] = lineaccount

                for i21 in range(0, len(myob_job)):
                    if 'TrackingName' in xero_spend_overpayment[i]['Line'][j]:
                        if xero_spend_overpayment[i]['Line'][j]['TrackingName'] == myob_job[i21]['Name']:
                            tracking['UID'] = myob_job[i21]['UID']
                            tracking['Name'] = myob_job[i21]['Name']
                            tracking['Number'] = myob_job[i21]['Number']

                if tracking != {} and tracking != None:
                    lineitem['Job'] = tracking
                else:
                    lineitem['Job'] = None

                taxrate1 = 0
                for j3 in range(0, len(taxcode_myob)):
                    for j2 in range(0, len(xero_tax)):
                        if xero_spend_overpayment[i]['Line'][j]['TaxType'] == xero_tax[j2]['TaxType']:
                            if xero_tax[j2]['TaxType'] in ['CAPEXINPUT', 'INPUT', 'OUTPUT']:
                                if taxcode_myob[j3]['Code'] == 'GST':
                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                    taxrate1 = taxcode_myob[j3]['Rate']

                            elif xero_tax[j2]['TaxType'] in ['EXEMPTCAPITAL', 'EXEMPTEXPENSES', 'EXEMPTEXPORT',
                                                             'EXEMPTOUTPUT']:
                                if taxcode_myob[j3]['Code'] == 'FRE':
                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                    taxrate1 = taxcode_myob[j3]['Rate']

                            elif xero_tax[j2]['TaxType'] in ["INPUTTAXED"]:
                                if taxcode_myob[j3]['Code'] == 'INP':
                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                    taxrate1 = taxcode_myob[j3]['Rate']

                            elif xero_tax[j2]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2"]:
                                if taxcode_myob[j3]['Code'] == 'N-T':
                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                    taxrate1 = taxcode_myob[j3]['Rate']
                        else:
                            if xero_spend_overpayment[i]['Line'][j]['TaxType'] in ["BASEXCLUDED", "BAS-W1", "BAS-W2",
                                                                                   "NONE"]:
                                if taxcode_myob[j3]['Code'] == 'N-T':
                                    taxcode['UID'] = taxcode_myob[j3]['UID']
                                    taxrate1 = taxcode_myob[j3]['Rate']

                lineitem['TaxCode'] = taxcode

                if xero_spend_overpayment[i]['LineAmountTypes'] == 'Inclusive':
                    Queryset1['IsTaxInclusive'] = True
                else:
                    Queryset1['IsTaxInclusive'] = False

                Queryset1['Lines'].append(lineitem)

            payload = json.dumps(Queryset1)
            id_or_name_value_for_error = (
                xero_spend_overpayment[i]['Reference']
                if xero_spend_overpayment[i]['Reference'] is not None
                else "")

            xero_spend_overpayment[i].pop("_id")
            xero_spend_overpayment[i].pop("job_id")
            xero_spend_overpayment[i].pop("is_pushed")
            xero_spend_overpayment[i].pop("error")
            xero_spend_overpayment[i].pop("task_id")
            xero_spend_overpayment[i].pop("table_name")

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/Banking/SpendMoneyTxn"
            asyncio.run(
                post_data_in_myob(url, headers, payload, spend_money_data, _id, job_id, task_id,
                                  id_or_name_value_for_error))


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
