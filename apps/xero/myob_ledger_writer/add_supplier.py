import asyncio
import json
import re

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_supplier_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        xero_supplier1 = dbname['xero_supplier']

        x = xero_supplier1.find({'job_id': job_id})
        data = []
        for k in x:
            data.append(k)

        taxcode = dbname['taxcode_myob'].find({'job_id': job_id})
        taxcode1 = []
        for p2 in taxcode:
            taxcode1.append(p2)

        for i in range(0, len(data)):

            _id = data[i]['_id']
            task_id = data[i]['task_id']
            Queryset = {'Addresses': []}
            Queryset2 = {}
            BuyingDetails = {}
            PaymentDetails = {}
            TaxCode = {}
            FreightTaxCode = {}
            ExpenseAccount = {}

            Queryset['IsIndividual'] = False
            Queryset["CompanyName"] = data[i]["Name"][0:50]
            if 'Details' in data[i]:
                Queryset['Notes'] = data[i]['Details']

            # Queryset["DisplayId"] = data[i]["ContactID"]
            if 'BankAccountDetails' in data[i]:
                data[i]["BankAccountDetails"] = re.sub("[^0-9]", "", data[i]["BankAccountDetails"])

            if "TaxNumber" in data[i]:
                if data[i]["TaxNumber"] != None and data[i]["TaxNumber"] != '':
                    data[i]["TaxNumber"] = data[i]["TaxNumber"].replace(" ", "")
                    BuyingDetails["ABN"] = data[i]["TaxNumber"][0:2] + " " + data[i]["TaxNumber"][2:5] + " " + data[i][
                                                                                                                   "TaxNumber"][
                                                                                                               5:8] + " " + \
                                           data[i]["TaxNumber"][8:11]

            if "BankAccNumber" in data[i]:
                banknumber = data[i]["BankAccNumber"].replace("-", "").strip()
                banknumber = banknumber.replace(" ", "")
                # PaymentDetails["BankAccountNumber"] = banknumber[0:2] + "-" + banknumber[2:6] + "-" + banknumber[6:13] + "-" + banknumber[13:]
                # PaymentDetails["BankAccountNumber"] = banknumber[6:]
                PaymentDetails["BankAccountNumber"] = None

            if "BankAccName" in data[i]:
                PaymentDetails["BankAccountName"] = data[i]["BankAccName"][0:20].upper()

            if "Details" in data[i]:
                PaymentDetails["StatementText"] = data[i]["Details"].upper()

            if 'BankAccountDetails' in data[i] and (
                    data[i]['BankAccountDetails'] != None and data[i]['BankAccountDetails'] != ""):
                PaymentDetails["BSBNumber"] = data[i]["BankAccountDetails"][0:3] + "-" + data[i]["BankAccountDetails"][
                                                                                         3:6]
            else:
                PaymentDetails["BSBNumber"] = None

            Queryset["PaymentDetails"] = PaymentDetails

            for j1 in range(0, len(taxcode1)):
                if taxcode1[j1]["Code"] == "N-T":
                    TaxCode['Code'] = taxcode1[j1]['Code']
                    TaxCode['UID'] = taxcode1[j1]['UID']
                    FreightTaxCode['Code'] = taxcode1[j1]['Code']
                    FreightTaxCode['UID'] = taxcode1[j1]['UID']

                    # ExpenseAccount["UID"] = taxcode1[j1]['UID']
            Queryset["BuyingDetails"] = BuyingDetails
            BuyingDetails['TaxCode'] = TaxCode
            BuyingDetails['FreightTaxCode'] = FreightTaxCode
            ExpenseAccount = None
            BuyingDetails['ExpenseAccount'] = ExpenseAccount

            for j in range(0, len(data[i]['Address'])):
                Queryset2 = {}
                if 'email' in data[i]:
                    Queryset2['Email'] = data[i]['email']
                if 'Website' in data[i]:
                    Queryset2['Website'] = data[i]['Website']

                Queryset2["ContactName"] = data[i]["Name"][0:25]
                if ('AddressLine2' in data[i]['Address'][j]) and ('AddressLine3' in data[i]['Address'][j]) and (
                        'AddressLine1' in data[i]['Address'][j]):
                    Queryset2['Street'] = data[i]['Address'][j]['AddressLine1'] + "," + data[i]['Address'][j][
                        'AddressLine2'] + "," + data[i]['Address'][j]['AddressLine3']
                elif ('AddressLine2' in data[i]['Address'][j]) and ('AddressLine1' in data[i]['Address'][j]):
                    Queryset2['Street'] = data[i]['Address'][j]['AddressLine1'] + "," + data[i]['Address'][j][
                        'AddressLine2']
                elif ('AddressLine1' in data[i]['Address'][j]):
                    Queryset2['Street'] = data[i]['Address'][j]['AddressLine1']

                if 'City' in data[i]['Address'][j]:
                    Queryset2['City'] = data[i]['Address'][j]['City']
                if 'Region' in data[i]['Address'][j]:
                    Queryset2['State'] = data[i]['Address'][j]['Region']
                if 'PostalCode' in data[i]['Address'][j]:
                    Queryset2['PostCode'] = data[i]['Address'][j]['PostalCode']
                if 'Country' in data[i]['Address'][j]:
                    Queryset2['Country'] = data[i]['Address'][j]['Country']

                Queryset['Addresses'].append(Queryset2)

                for j1 in range(0, len(data[i]['Phone'])):

                    if "PhoneNumber" in data[i]['Phone'][j1]:
                        if data[i]['Phone'][j1]['PhoneType'] == 'FAX':
                            Queryset2['Fax'] = data[i]['Phone'][j1]["PhoneNumber"][0:21]
                        if data[i]['Phone'][j1]['PhoneType'] == 'DDI':
                            Queryset2['Phone1'] = data[i]['Phone'][j1]["PhoneNumber"][0:21]
                        if data[i]['Phone'][j1]['PhoneType'] == 'DEFAULT':
                            Queryset2['Phone2'] = data[i]['Phone'][j1]["PhoneNumber"][0:21]
                        if data[i]['Phone'][j1]['PhoneType'] == 'MOBILE':
                            Queryset2['Phone3'] = data[i]['Phone'][j1]["PhoneNumber"][0:21]

            payload = json.dumps(Queryset)

            id_or_name_value_for_error = (
                data[i]["Name"]
                if data[i]["Name"] is not None
                else None)

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/Contact/Supplier"
            if data[i]['is_pushed'] == 0:
                asyncio.run(
                    post_data_in_myob(url, headers, payload, xero_supplier1, _id, job_id, task_id,
                                      id_or_name_value_for_error))

            else:
                pass



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
