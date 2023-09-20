import asyncio
import json

from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_customer_to_myobledger(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        payload = {}

        xero_customer = dbname['xero_customer']

        x = xero_customer.find({'job_id': job_id})
        data = []
        for k in x:
            data.append(k)

        taxcode = dbname['taxcode_myob'].find({'job_id': job_id})
        taxcode1 = []
        for p2 in taxcode:
            taxcode1.append(p2)

        data=data

        for i in range(0, len(data)):
           
            
            _id = data[i]['_id']
            task_id = data[i]['task_id']
            Queryset = {'Addresses': []}
            Queryset2 = {}
            SellingDetails = {}
            IncomeAccount = {}
            TaxCode = {}
            FreightTaxCode = {}

            Queryset['IsIndividual'] = False
            Queryset["CompanyName"] = data[i]["Name"][0:50]

            if 'TaxNumber' in data[i]:
                if data[i]["TaxNumber"] != None and data[i]["TaxNumber"] != '':
                    taxnumber = data[i]["TaxNumber"].replace(" ", "")
                    SellingDetails["ABN"] = taxnumber[0:2] + " " + taxnumber[2:5] + " " + taxnumber[
                                                                                          5:8] + " " + taxnumber[8:11]
                    # SellingDetails["ABN"]=data[i]["TaxNumber"]
            for j1 in range(0, len(taxcode1)):
                if taxcode1[j1]["Code"] == "N-T":
                    TaxCode['Code'] = taxcode1[j1]['Code']
                    TaxCode['UID'] = taxcode1[j1]['UID']
                    FreightTaxCode['Code'] = taxcode1[j1]['Code']
                    FreightTaxCode['UID'] = taxcode1[j1]['UID']

            Queryset["SellingDetails"] = SellingDetails
            SellingDetails['TaxCode'] = TaxCode
            SellingDetails['FreightTaxCode'] = FreightTaxCode

            for j in reversed(range(0, len(data[i]['Address']))):
                Queryset2 = {}
                if 'email' in data[i]:
                    Queryset2['Email'] = data[i]['email']
                if 'Website' in data[i]:
                    Queryset2['Website'] = data[i]['Website']

                Queryset2["ContactName"] = data[i]["Name"][0:25]
                if ('AddressLine2' in data[i]['Address'][j]) and ('AddressLine3' in data[i]['Address'][j]) and ('AddressLine1' in data[i]['Address'][j]):
                    Queryset2['Street'] = data[i]['Address'][j]['AddressLine1'] + "," + data[i]['Address'][j][
                        'AddressLine2'] + "," + data[i]['Address'][j]['AddressLine3']
                elif ('AddressLine2' in data[i]['Address'][j]) and ('AddressLine1' in data[i]['Address'][j]):
                    Queryset2['Street'] = data[i]['Address'][j]['AddressLine1'] + "," + data[i]['Address'][j][
                        'AddressLine2']
                elif ('AddressLine1' in data[i]['Address'][j]):
                    Queryset2['Street'] = data[i]['Address'][j]['AddressLine1']

                else:
                    if "AddressType" in data[i]["Address"][j]:
                        Queryset2['Street'] = data[i]['Address'][j]['AddressType']

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
            print(payload)
            id_or_name_value_for_error = (
                data[i]['Name']
                if data[i]['Name'] is not None
                else "")

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/Contact/Customer"

            if  data[i]['is_pushed']==0:
                asyncio.run(
                    post_data_in_myob(url, headers, payload, xero_customer, _id, job_id, task_id,
                                    id_or_name_value_for_error))  
            else:
                pass


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
