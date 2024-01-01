import json
import logging

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo

import logging


def get_used_archived_suppliers(job_id, task_id):
    try:
        logging.info("Started executing xero -> qbowriter ->  get_used_archived_suppliers")
        dbname = get_mongodb_database()
        xero_archived_supplier_in_bill1 = dbname['xero_archived_supplier_in_bill']

        contacts1 = set(
            [doc["ContactName"] for doc in dbname['xero_bill_suppliers'].find({'job_id': job_id}, {"ContactName": 1})])
        contacts2 = list(dbname['xero_archived_supplier'].find({'job_id': job_id}))

        filtered_contacts2 = [doc for doc in contacts2 if any(doc['Name'].startswith(contact) for contact in contacts1)]
        result = filtered_contacts2
        if len(result) > 0:
            xero_archived_supplier_in_bill1.insert_many(result)

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> get_used_archived_customers", ex)


def add_xero_archieved_supplier(job_id, task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_supplier -> add_xero_archived_supplier")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/vendor?minorversion=40"

        supplier_data = dbname["xero_archived_supplier_in_bill"]

        suppliers = supplier_data.find({"job_id": job_id})

        for supplier in suppliers:
            _id = supplier.get('_id')
            task_id = supplier.get('task_id')
            QuerySet2 = {}
            QuerySet3 = {}
            QuerySet4 = {}
            QuerySet6 = {}
            QuerySet7 = {}
            QuerySet8 = {}
            QuerySet9 = {}
            QuerySet10 = {}

            if supplier.get("BankAccountDetails") is not None and supplier.get("BankAccountDetails") is not "":
                QuerySet2["AcctNum"] = supplier.get("BankAccountDetails")[7:]

            QuerySet2["TaxIdentifier"] = supplier.get("TaxNumber")

            QuerySet2["GivenName"] = supplier.get("FirstName").replace(":", "-") if supplier.get(
                "FirstName") != None else None
            QuerySet2["FamilyName"] = supplier.get("LastName").replace(":", "-") if supplier.get(
                "LasttName") != None else None
            if len(supplier.get("Address")) != 0:
                supplier_address = supplier.get("Address")
                QuerySet3["Line1"] = supplier_address[0].get("Region")
                QuerySet3["City"] = supplier_address[0].get("City")
                QuerySet3["PostalCode"] = supplier_address[0].get("PostalCode")
            if len(supplier.get("Phone")) != 0:
                supplier_phone = supplier.get("Phone")
                QuerySet4["FreeFormNumber"] = supplier_phone[1].get("PhoneNumber")
                QuerySet8["FreeFormNumber"] = supplier_phone[2].get("PhoneNumber")
                QuerySet7["FreeFormNumber"] = supplier_phone[3].get("PhoneNumber")

            QuerySet2["DisplayName"] = supplier.get("Name").replace(":", "-") if supplier.get("Name") != None else None
            QuerySet2["PrintOnCheckName"] = QuerySet2["DisplayName"][0:110]

            QuerySet10["URI"] = supplier.get("Website")
            QuerySet6["Address"] = supplier.get("email")

            QuerySet2["BillAddr"] = QuerySet3
            QuerySet2["PrimaryPhone"] = QuerySet4
            QuerySet2["Mobile"] = QuerySet7
            QuerySet2["Fax"] = QuerySet8
            QuerySet2["AlternatePhone"] = QuerySet7
            QuerySet2["PrimaryEmailAddr"] = QuerySet6
            QuerySet2["WebAddr"] = QuerySet10

            QuerySet9["BankAccountName"] = supplier.get("BankAccName")

            if supplier.get("BankAccNumber") is not None and supplier.get("BankAccNumber") is not "":
                QuerySet9["BankBranchIdentifier"] = (
                        supplier.get("BankAccNumber")[0:3]
                        + "-"
                        + supplier.get("BankAccNumber")[3:6]
                )

            if supplier.get("BankAccNumber") is not None and supplier.get("BankAccNumber") is not "":
                QuerySet9["BankAccountNumber"] = supplier.get("BankAccNumber")[6:16]

            QuerySet9["StatementText"] = supplier.get("Details")

            if len(QuerySet9) == 0:
                pass
            elif len(QuerySet9) == 4:
                QuerySet2["VendorPaymentBankDetail"] = QuerySet9

            payload = json.dumps(QuerySet2)

            post_data_in_qbo(url, headers, payload, supplier_data, _id, job_id, task_id, supplier.get("Name"))


    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_supplier -> add_xero_archived_supplier", ex)
