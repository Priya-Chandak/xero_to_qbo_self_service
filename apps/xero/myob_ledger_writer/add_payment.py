import json
from datetime import datetime

import requests

from apps.home.data_util import add_job_status, get_job_details
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database


def add_invoice_payment_as_receive_money(job_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        dbname = get_mongodb_database()
        tool1 = aliased(Tool)
        tool2 = aliased(Tool)

        # jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),tool2.account_type.label('output_tool')).join(tool1, Jobs.input_account_id == tool1.id).join(tool2, Jobs.output_account_id == tool2.id).filter(Jobs.id == job_id).first()
        jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),
                                                         tool2.account_type.label('output_tool')
                                                         ).join(tool1, Jobs.input_account_id == tool1.id
                                                                ).join(tool2, Jobs.output_account_id == tool2.id
                                                                       ).filter(Jobs.id == job_id).first()
        if (input_tool == MYOB):
            payload, base_url, headers = get_myob_settings(job_id)
        elif (output_tool == MYOB):
            payload, base_url, headers = post_myob_settings(job_id)

        if (input_tool == MYOBLEDGER):
            payload, base_url, headers = get_myobledger_settings(job_id)
        elif (output_tool == MYOBLEDGER):
            payload, base_url, headers = post_myobledger_settings(job_id)

        url = f"{base_url}/Banking/ReceiveMoneyTxn"

        # invoice_payment = dbname['xero_invoice_payment'].find({"job_id": job_id})
        invoice_payment = dbname['xero_billcredit_payment'].find({"job_id": job_id})
        xero_invoice_payment = []
        for p1 in invoice_payment:
            xero_invoice_payment.append(p1)

        invoice_batchpayment = dbname['xero_invoice_batchpayment'].find({"job_id": job_id})
        xero_invoice_batchpayment = []
        for p11 in invoice_batchpayment:
            xero_invoice_batchpayment.append(p11)

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
        for k7 in range(0, dbname['taxcode_myob'].count_documents({})):
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

        xero_invoice1 = dbname['xero_invoice'].find({"job_id": job_id})
        xero_invoice = []
        for p9 in xero_invoice1:
            xero_invoice.append(p9)

        xero_invoice_payment = xero_invoice_payment

        for i in range(0, len(xero_invoice_payment)):
            if xero_invoice_payment[i]['Type'] != "RECBATCH":
                print(xero_invoice_payment[i])
                Queryset1 = {'Lines': []}
                account = {}
                contact = {}

                for i1 in range(0, len(xero_coa)):
                    for i2 in range(0, len(myob_coa)):
                        if xero_invoice_payment[i]['AccountCode'] == xero_coa[i1]['AccountID']:
                            if xero_coa[i1]['Name'] == myob_coa[i2]['Name']:
                                account['UID'] = myob_coa[i2]['UID']
                                account['Name'] = myob_coa[i2]['Name']

                Queryset1['account'] = account

                for i3 in range(0, len(myob_supplier)):
                    if xero_invoice_payment[i]['Contact'] == myob_supplier[i3]['DisplayName']:
                        contact['UID'] = myob_supplier[i3]['UID']
                        contact['Name'] = myob_supplier[i3]['DisplayName']
                        contact['Type'] = 'Supplier'
                    elif myob_supplier[i3]['FirstName'].startswith(xero_invoice_payment[i]['Contact']) and \
                            myob_supplier[i3]['FirstName'].endswith("- C"):
                        contact['UID'] = myob_supplier[i3]['UID']
                        contact['Name'] = myob_supplier[i3]['DisplayName']
                        contact['Type'] = 'Supplier'
                    else:
                        contact['UID'] = "aaf38a3f-8bf3-4625-8875-7c96930c44c8"
                        contact['Type'] = 'Supplier'

                Queryset1['Contact'] = contact

                Queryset1['ReceiptNumber'] = xero_invoice_payment[i]['InvoiceNumber']
                Queryset1['DepositTo'] = "account"
                invoice_date = xero_invoice_payment[i]["Date"]
                invoice_date11 = int(invoice_date[6:16])
                invoice_date12 = datetime.utcfromtimestamp(invoice_date11).strftime('%Y-%m-%d')
                Queryset1['Date'] = invoice_date12
                Queryset1['AmountPaid'] = xero_invoice_payment[i]['Amount']
                # Queryset1['TotalTax']=xero_invoice_payment[i]['TotalTax']

                lineitem = {}
                lineaccount = {}
                taxcode = {}
                tracking = {}
                lineitem['Amount'] = xero_invoice_payment[i]['Amount']
                lineitem['Memo'] = xero_invoice_payment[i]['Reference']
                lineitem['UnitCount'] = 1

                for i2 in range(0, len(myob_coa)):
                    if myob_coa[i2]['Name'] == 'Accounts Receivable':
                        lineaccount['UID'] = myob_coa[i2]["UID"]

                lineitem['account'] = lineaccount

                taxrate1 = 0
                for j3 in range(0, len(taxcode_myob)):
                    for j2 in range(0, len(xero_tax)):
                        if taxcode_myob[j3]['Code'] == 'N-T':
                            taxcode['UID'] = taxcode_myob[j3]['UID']
                            taxrate1 = taxcode_myob[j3]['Rate']

                lineitem['TaxCode'] = taxcode
                Queryset1['IsTaxInclusive'] = False

                Queryset1['Lines'].append(lineitem)

                payload = json.dumps(Queryset1)
                print(payload)

                response = requests.request("POST", url, headers=headers, data=payload)
                print(response)
                print("------------------------------------")

                if response.status_code == 401:
                    res1 = json.loads(response.text)
                    res2 = ((res1['fault']['error'][0]['message']).split(";")[0]).split("=")[
                               1] + ': Please Update the Access Token'
                    add_job_status(job_id, "error")
                elif response.status_code == 400:
                    res1 = json.loads(response.text)
                    res2 = (res1['Errors'][0]['Message'])
                    add_job_status(job_id, res1, "error")

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex, "error")
        print(ex)


def add_invoice_batchpayment_as_receive_money(job_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        dbname = get_mongodb_database()
        tool1 = aliased(Tool)
        tool2 = aliased(Tool)

        # jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),tool2.account_type.label('output_tool')).join(tool1, Jobs.input_account_id == tool1.id).join(tool2, Jobs.output_account_id == tool2.id).filter(Jobs.id == job_id).first()
        jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),
                                                         tool2.account_type.label('output_tool')
                                                         ).join(tool1, Jobs.input_account_id == tool1.id
                                                                ).join(tool2, Jobs.output_account_id == tool2.id
                                                                       ).filter(Jobs.id == job_id).first()
        if (input_tool == MYOB):
            payload, base_url, headers = get_myob_settings(job_id)
        elif (output_tool == MYOB):
            payload, base_url, headers = post_myob_settings(job_id)

        if (input_tool == MYOBLEDGER):
            payload, base_url, headers = get_myobledger_settings(job_id)
        elif (output_tool == MYOBLEDGER):
            payload, base_url, headers = post_myobledger_settings(job_id)

        url = f"{base_url}/Banking/ReceiveMoneyTxn"

        invoice_payment = dbname['xero_invoice_payment'].find({"job_id": job_id})
        xero_invoice_payment = []
        for p1 in invoice_payment:
            xero_invoice_payment.append(p1)

        invoice_batchpayment = dbname['xero_invoice_batchpayment'].find({"job_id": job_id})
        xero_invoice_batchpayment = []
        for p11 in invoice_batchpayment:
            xero_invoice_batchpayment.append(p11)

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
        for k7 in range(0, dbname['taxcode_myob'].count_documents({})):
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

        xero_invoice1 = dbname['xero_invoice'].find({"job_id": job_id})
        xero_invoice = []
        for p9 in xero_invoice1:
            xero_invoice.append(p9)

        xero_invoice_batchpayment = xero_invoice_batchpayment

        for i in range(0, len(xero_invoice_batchpayment)):
            Queryset1 = {'Lines': []}
            account = {}
            contact = {}
            # Queryset1['Memo']=xero_invoice_batchpayment[i]['BatchPaymentID']

            for i1 in range(0, len(xero_coa)):
                for i2 in range(0, len(myob_coa)):
                    if xero_invoice_batchpayment[i]['account']['AccountID'] == xero_coa[i1]['AccountID']:
                        if xero_coa[i1]['Name'] == myob_coa[i2]['Name']:
                            account['UID'] = myob_coa[i2]['UID']
                            account['Name'] = myob_coa[i2]['Name']

            Queryset1['account'] = account

            for i4 in range(0, len(xero_invoice_payment)):
                if 'BatchPaymentID' in xero_invoice_payment[i4]:
                    if xero_invoice_batchpayment[i]['BatchPaymentID'] == xero_invoice_payment[i4]['BatchPaymentID']:
                        for i3 in range(0, len(myob_supplier)):
                            if xero_invoice_payment[i4]['Contact'] == myob_supplier[i3]['DisplayName']:
                                contact['UID'] = myob_supplier[i3]['UID']
                                contact['Name'] = myob_supplier[i3]['DisplayName']
                                contact['Type'] = 'Supplier'
                            elif myob_supplier[i3]['FirstName'].startswith(xero_invoice_payment[i4]['Contact']) and \
                                    myob_supplier[i3]['FirstName'].endswith("- S"):
                                contact['UID'] = myob_supplier[i3]['UID']
                                contact['Name'] = myob_supplier[i3]['DisplayName']
                                contact['Type'] = 'Supplier'

                        for i5 in range(0, len(myob_customer)):
                            if 'Company_Name' in myob_customer[i5] and myob_customer[i5]['Company_Name'] != None:

                                if xero_invoice_payment[i4]['Contact'] == myob_customer[i5]['Company_Name']:
                                    contact['UID'] = myob_customer[i5]['UID']
                                    contact['Name'] = myob_customer[i5]['Company_Name']
                                    contact['Type'] = 'Customer'
                                elif myob_customer[i5]['Company_Name'].startswith(xero_invoice_payment[i4]['Contact']):
                                    contact['UID'] = myob_customer[i5]['UID']
                                    contact['Name'] = myob_customer[i5]['Company_Name']
                                    contact['Type'] = 'Customer'

            Queryset1['Contact'] = contact
            if 'Docnumber' in xero_invoice_batchpayment[i]:
                Queryset1['ReceiptNumber'] = xero_invoice_batchpayment[i]['Docnumber'][-2:]
            else:
                Queryset1['ReceiptNumber'] = "NA"
            Queryset1['DepositTo'] = "account"
            invoice_date = xero_invoice_batchpayment[i]["Date"]
            invoice_date11 = int(invoice_date[6:16])
            invoice_date12 = datetime.utcfromtimestamp(invoice_date11).strftime('%Y-%m-%d')
            Queryset1['Date'] = invoice_date12
            Queryset1['AmountPaid'] = xero_invoice_batchpayment[i]['TotalAmount']
            # Queryset1['TotalTax']=xero_invoice_batchpayment[i]['TotalTax']

            for j in range(0, len(xero_invoice_batchpayment[i]['Payments'])):
                lineitem = {}
                lineaccount = {}
                taxcode = {}
                tracking = {}
                lineitem['Amount'] = xero_invoice_batchpayment[i]['Payments'][j]['Amount']
                for j2 in range(0, len(xero_invoice)):
                    if xero_invoice_batchpayment[i]['Payments'][j]['Invoice']['InvoiceID'] == xero_invoice[j2][
                        'Inv_ID']:
                        lineitem['Memo'] = xero_invoice[j2]['Inv_No']

                lineitem['UnitCount'] = 1

                for i2 in range(0, len(myob_coa)):
                    if myob_coa[i2]['Name'] == 'Accounts Receivable':
                        lineaccount['UID'] = myob_coa[i2]["UID"]

                lineitem['account'] = lineaccount

                #     elif xero_tax[j2]['TaxType'] in ["INPUTTAXED"]:
                #         if taxcode_myob[j3]['Code']=='INP':
                #             taxcode['UID']=taxcode_myob[j3]['UID']
                #             taxrate1 = taxcode_myob[j3]['Rate']

                #     elif xero_tax[j2]['TaxType'] in ["INPUTTAXED"]:
                #         if taxcode_myob[j3]['Code']=='INP':
                #             taxcode['UID']=taxcode_myob[j3]['UID']
                #             taxrate1 = taxcode_myob[j3]['Rate']

                taxrate1 = 0
                for j3 in range(0, len(taxcode_myob)):
                    for j2 in range(0, len(xero_tax)):
                        if taxcode_myob[j3]['Code'] == 'N-T':
                            taxcode['UID'] = taxcode_myob[j3]['UID']
                            taxrate1 = taxcode_myob[j3]['Rate']

                lineitem['TaxCode'] = taxcode
                Queryset1['IsTaxInclusive'] = False

                Queryset1['Lines'].append(lineitem)

            payload = json.dumps(Queryset1)
            print(payload)

            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            print("------------------------------------")

            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = ((res1['fault']['error'][0]['message']).split(";")[0]).split("=")[
                           1] + ': Please Update the Access Token'
                add_job_status(job_id, "error")
            elif response.status_code == 400:
                res1 = json.loads(response.text)
                res2 = (res1['Errors'][0]['Message'])
                add_job_status(job_id, res1, "error")

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex, "error")
        print(ex)


def add_bill_payment_as_spend_money(job_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        dbname = get_mongodb_database()
        tool1 = aliased(Tool)
        tool2 = aliased(Tool)

        # jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),tool2.account_type.label('output_tool')).join(tool1, Jobs.input_account_id == tool1.id).join(tool2, Jobs.output_account_id == tool2.id).filter(Jobs.id == job_id).first()
        jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),
                                                         tool2.account_type.label('output_tool')
                                                         ).join(tool1, Jobs.input_account_id == tool1.id
                                                                ).join(tool2, Jobs.output_account_id == tool2.id
                                                                       ).filter(Jobs.id == job_id).first()
        if (input_tool == MYOB):
            payload, base_url, headers = get_myob_settings(job_id)
        elif (output_tool == MYOB):
            payload, base_url, headers = post_myob_settings(job_id)

        if (input_tool == MYOBLEDGER):
            payload, base_url, headers = get_myobledger_settings(job_id)
        elif (output_tool == MYOBLEDGER):
            payload, base_url, headers = post_myobledger_settings(job_id)

        url = f"{base_url}/Banking/SpendMoneyTxn"

        bill_payment = dbname['xero_creditnote_payment'].find({"job_id": job_id})
        # bill_payment = dbname['xero_bill_payment'].find({"job_id": job_id})

        xero_bill_payment = []
        for p1 in bill_payment:
            xero_bill_payment.append(p1)

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
        for k7 in range(0, dbname['taxcode_myob'].count_documents({})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

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

        xero_bill_payment = xero_bill_payment

        for i in range(0, len(xero_bill_payment)):
            print(xero_bill_payment[i])
            Queryset1 = {'Lines': []}
            account = {}
            contact = {}

            for i1 in range(0, len(xero_coa)):
                for i2 in range(0, len(myob_coa)):
                    if xero_bill_payment[i]['AccountCode'] == xero_coa[i1]['AccountID']:
                        if xero_coa[i1]['Name'] == myob_coa[i2]['Name']:
                            account['UID'] = myob_coa[i2]['UID']
                            account['Name'] = myob_coa[i2]['Name']

            Queryset1['account'] = account

            for i3 in range(0, len(myob_customer)):
                if 'DisplayName' in myob_customer[i3]:
                    if xero_bill_payment[i]['Contact'] == myob_customer[i3]['DisplayName']:
                        contact['UID'] = myob_customer[i3]['UID']
                        contact['Name'] = myob_customer[i3]['DisplayName']
                        contact['Type'] = 'Customer'
                elif 'FirstName' in myob_customer[i3] and myob_customer[i3]['FirstName'] != None:
                    if myob_customer[i3]['FirstName'].startswith(xero_bill_payment[i]['Contact']) and myob_customer[i3][
                        'FirstName'].endswith("- C"):
                        contact['UID'] = myob_customer[i3]['UID']
                        contact['Name'] = myob_customer[i3]['DisplayName']
                        contact['Type'] = 'Customer'
                elif myob_customer[i3]['Company_Name'].startswith(xero_bill_payment[i]['Contact']) and \
                        myob_customer[i3]['Company_Name'].endswith("- C"):
                    contact['UID'] = myob_customer[i3]['UID']
                    contact['Name'] = myob_customer[i3]['Company_Name']
                    contact['Type'] = 'Customer'

            # for i31 in range(0,len(myob_customer)):
            #     if xero_invoice_payment[i]['ContactName'] == myob_supplier[i3]['DisplayName'] :
            #         contact['UID'] = myob_supplier[i3]['UID']
            #         contact['Name'] = myob_supplier[i3]['DisplayName']
            #         contact['Type'] = 'Customer'

            Queryset1['Contact'] = contact

            Queryset1['PaymentNumber'] = xero_bill_payment[i]['InvoiceNumber']
            Queryset1['PayFrom'] = "account"
            invoice_date = xero_bill_payment[i]["Date"]
            invoice_date11 = int(invoice_date[6:16])
            invoice_date12 = datetime.utcfromtimestamp(invoice_date11).strftime('%Y-%m-%d')
            Queryset1['Date'] = invoice_date12
            Queryset1['AmountPaid'] = xero_bill_payment[i]['Amount']
            # Queryset1['TotalTax']=xero_bill_payment[i]['TotalTax']

            lineitem = {}
            lineaccount = {}
            taxcode = {}
            tracking = {}
            lineitem['Amount'] = xero_bill_payment[i]['Amount']
            # lineitem['Memo']=xero_bill_payment[i]['Reference']
            lineitem['UnitCount'] = 1

            for i2 in range(0, len(myob_coa)):
                if myob_coa[i2]['Name'] == 'Accounts Payable':
                    lineaccount['UID'] = myob_coa[i2]["UID"]

            lineitem['account'] = lineaccount

            taxrate1 = 0
            for j3 in range(0, len(taxcode_myob)):
                for j2 in range(0, len(xero_tax)):
                    if taxcode_myob[j3]['Code'] == 'N-T':
                        taxcode['UID'] = taxcode_myob[j3]['UID']
                        taxrate1 = taxcode_myob[j3]['Rate']

            lineitem['TaxCode'] = taxcode
            Queryset1['IsTaxInclusive'] = False

            Queryset1['Lines'].append(lineitem)

            payload = json.dumps(Queryset1)
            print(payload)

            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            print("------------------------------------")

            if response.status_code == 401:
                res1 = json.loads(response.text)
                res2 = ((res1['fault']['error'][0]['message']).split(";")[0]).split("=")[
                           1] + ': Please Update the Access Token'
                add_job_status(job_id, "error")
            elif response.status_code == 400:
                res1 = json.loads(response.text)
                res2 = (res1['Errors'][0]['Message'])
                add_job_status(job_id, res1, "error")

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex, "error")
        print(ex)


def add_bill_batchpayment_as_spend_money(job_id):
    try:
        start_date, end_date = get_job_details(job_id)
        if (start_date != '' and end_date != ''):
            start_date1 = datetime.strptime(start_date, '%Y-%m-%d')
            end_date1 = datetime.strptime(end_date, '%Y-%m-%d')

        dbname = get_mongodb_database()
        tool1 = aliased(Tool)
        tool2 = aliased(Tool)

        # jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),tool2.account_type.label('output_tool')).join(tool1, Jobs.input_account_id == tool1.id).join(tool2, Jobs.output_account_id == tool2.id).filter(Jobs.id == job_id).first()
        jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),
                                                         tool2.account_type.label('output_tool')
                                                         ).join(tool1, Jobs.input_account_id == tool1.id
                                                                ).join(tool2, Jobs.output_account_id == tool2.id
                                                                       ).filter(Jobs.id == job_id).first()
        if (input_tool == MYOB):
            payload, base_url, headers = get_myob_settings(job_id)
        elif (output_tool == MYOB):
            payload, base_url, headers = post_myob_settings(job_id)

        if (input_tool == MYOBLEDGER):
            payload, base_url, headers = get_myobledger_settings(job_id)
        elif (output_tool == MYOBLEDGER):
            payload, base_url, headers = post_myobledger_settings(job_id)

        url = f"{base_url}/Banking/SpendMoneyTxn"

        bill_payment = dbname['xero_bill_payment'].find({"job_id": job_id})
        xero_bill_payment = []
        for p1 in bill_payment:
            xero_bill_payment.append(p1)

        bill_batchpayment = dbname['xero_bill_batchpayment'].find({"job_id": job_id})
        xero_bill_batchpayment = []
        for p11 in bill_batchpayment:
            xero_bill_batchpayment.append(p11)

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
        for k7 in range(0, dbname['taxcode_myob'].count_documents({})):
            taxcode_myob.append(taxcode_myob1[k7])

        xero_tax1 = dbname['xero_taxrate'].find({"job_id": job_id})
        xero_tax = []
        for p5 in xero_tax1:
            xero_tax.append(p5)

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

        xero_bill1 = dbname['xero_bill'].find({"job_id": job_id})
        xero_bill = []
        for p8 in xero_bill1:
            xero_bill.append(p8)

        xero_bill_batchpayment = xero_bill_batchpayment

        for i in range(0, len(xero_bill_batchpayment)):
            if xero_bill_batchpayment[i]['Status'] != 'DELETED' and xero_bill_batchpayment[i]['Status'] != 'VOIDED':
                print(xero_bill_batchpayment[i])
                print("--")
                Queryset1 = {'Lines': []}
                account = {}
                contact = {}

                for i1 in range(0, len(xero_coa)):
                    for i2 in range(0, len(myob_coa)):
                        if xero_bill_batchpayment[i]['account']['AccountID'] == xero_coa[i1]['AccountID']:
                            if xero_coa[i1]['Name'] == myob_coa[i2]['Name']:
                                account['UID'] = myob_coa[i2]['UID']
                                account['Name'] = myob_coa[i2]['Name']

                Queryset1['account'] = account

                for i4 in range(0, len(xero_bill_payment)):
                    if 'BatchPaymentID' in xero_bill_payment[i4]:
                        if xero_bill_batchpayment[i]['BatchPaymentID'] == xero_bill_payment[i4]['BatchPaymentID']:

                            for i3 in range(0, len(myob_customer)):
                                if 'DisplayName' in myob_customer[i3]:
                                    if xero_bill_payment[i4]['Contact'] == myob_customer[i3]['DisplayName']:
                                        contact['UID'] = myob_customer[i3]['UID']
                                        contact['Name'] = myob_customer[i3]['DisplayName']
                                        contact['Type'] = 'Customer'
                                elif 'FirstName' in myob_customer[i3] and myob_customer[i3]['FirstName'] != None:
                                    if myob_customer[i3]['FirstName'].startswith(xero_bill_payment[i4]['Contact']) and \
                                            myob_customer[i3]['FirstName'].endswith("- C"):
                                        contact['UID'] = myob_customer[i3]['UID']
                                        contact['Name'] = myob_customer[i3]['DisplayName']
                                        contact['Type'] = 'Customer'
                                elif myob_customer[i3]['Company_Name'].startswith(xero_bill_payment[i]['Contact']) and \
                                        myob_customer[i3]['Company_Name'].endswith("- C"):
                                    contact['UID'] = myob_customer[i3]['UID']
                                    contact['Name'] = myob_customer[i3]['Company_Name']
                                    contact['Type'] = 'Customer'

                Queryset1['Contact'] = contact

                Queryset1['PaymentNumber'] = xero_bill_batchpayment[i]['BatchPaymentID'][-4:]
                Queryset1['PayFrom'] = "account"
                invoice_date = xero_bill_batchpayment[i]["Date"]
                invoice_date11 = int(invoice_date[6:16])
                invoice_date12 = datetime.utcfromtimestamp(invoice_date11).strftime('%Y-%m-%d')
                Queryset1['Date'] = invoice_date12
                Queryset1['AmountPaid'] = xero_bill_batchpayment[i]['TotalAmount']
                # Queryset1['TotalTax']=xero_bill_payment[i]['TotalTax']

                for j in range(0, len(xero_bill_batchpayment[i]['Payments'])):
                    lineitem = {}
                    lineaccount = {}
                    taxcode = {}
                    tracking = {}
                    lineitem['Amount'] = xero_bill_batchpayment[i]['Payments'][j]['Amount']
                    for j2 in range(0, len(xero_bill)):
                        if xero_bill_batchpayment[i]['Payments'][j]['Invoice']['InvoiceID'] == xero_bill[j2]['Inv_ID']:
                            lineitem['Memo'] = xero_bill[j2]['Inv_No']

                    lineitem['UnitCount'] = 1

                    for i2 in range(0, len(myob_coa)):
                        if myob_coa[i2]['Name'] == 'Accounts Payable':
                            lineaccount['UID'] = myob_coa[i2]["UID"]

                    lineitem['account'] = lineaccount

                    taxrate1 = 0
                    for j3 in range(0, len(taxcode_myob)):
                        for j2 in range(0, len(xero_tax)):
                            if taxcode_myob[j3]['Code'] == 'N-T':
                                taxcode['UID'] = taxcode_myob[j3]['UID']
                                taxrate1 = taxcode_myob[j3]['Rate']

                    lineitem['TaxCode'] = taxcode
                    Queryset1['IsTaxInclusive'] = False

                    Queryset1['Lines'].append(lineitem)

                payload = json.dumps(Queryset1)
                print(payload)

                response = requests.request("POST", url, headers=headers, data=payload)
                print(response)
                print("------------------------------------")

                if response.status_code == 401:
                    res1 = json.loads(response.text)
                    res2 = ((res1['fault']['error'][0]['message']).split(";")[0]).split("=")[
                               1] + ': Please Update the Access Token'
                    add_job_status(job_id, "error")
                elif response.status_code == 400:
                    res1 = json.loads(response.text)
                    res2 = (res1['Errors'][0]['Message'])
                    add_job_status(job_id, res1, "error")


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        add_job_status(job_id, ex, "error")
        print(ex)
