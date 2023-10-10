import json
import logging
import re

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo

logger = logging.getLogger(__name__)


def add_xero_supplier(job_id, task_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_supplier -> add_xero_supplier")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/vendor?minorversion=40"

        supplier_data = dbname["xero_supplier"]

        suppliers = supplier_data.find({"job_id": job_id})

        for supplier in suppliers:
            supplier_address = supplier.get("Address")
            supplier_phone = supplier.get("Phone")
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

            if supplier.get("BankAccountDetails") is not None:
                QuerySet2["AcctNum"] = supplier.get("BankAccountDetails")[7:]

            QuerySet2["TaxIdentifier"] = supplier.get("TaxNumber")

            QuerySet2["GivenName"] = supplier.get("FirstName").replace(":", "-") if supplier.get(
                "FirstName") != None else None
            QuerySet2["FamilyName"] = supplier.get("LastName").replace(":", "-") if supplier.get(
                "LasttName") != None else None

            QuerySet2["DisplayName"] = supplier.get("Name").replace(":", "-") if supplier.get("Name") != None else None
            QuerySet2["PrintOnCheckName"] = QuerySet2["DisplayName"][0:110]

            QuerySet3["Line1"] = supplier_address[0].get("Region")

            QuerySet3["City"] = supplier_address[0].get("City")
            QuerySet3["PostalCode"] = supplier_address[0].get("PostalCode")

            QuerySet4["FreeFormNumber"] = supplier_phone[1].get("PhoneNumber")
            QuerySet8["FreeFormNumber"] = supplier_phone[2].get("PhoneNumber")
            QuerySet7["FreeFormNumber"] = supplier_phone[3].get("PhoneNumber")

            if supplier.get("Website") != None:
                QuerySet10["URI"] = supplier.get("Website") if supplier.get("Website").startswith(
                    "http") else 'https://' + supplier.get("Website")
            else:
                QuerySet10["URI"] = None
            QuerySet6["Address"] = supplier.get("email")

            QuerySet2["BillAddr"] = QuerySet3
            QuerySet2["PrimaryPhone"] = QuerySet4
            QuerySet2["Mobile"] = QuerySet7
            QuerySet2["Fax"] = QuerySet8
            QuerySet2["AlternatePhone"] = QuerySet7
            QuerySet2["PrimaryEmailAddr"] = QuerySet6
            QuerySet2["WebAddr"] = QuerySet10 if QuerySet10["URI"] != None else None

            if supplier.get("BankAccName") not in ["", None]:
                QuerySet9["BankAccountName"] = supplier.get("BankAccName")
            else:
                QuerySet9["BankAccountName"] = "NA"

            if supplier.get("BankAccNumber") not in ["", None]:
                pattern = r'^\d{3}-\d{3}$'
                if re.match(pattern, supplier.get("BankAccNumber")):
                    QuerySet9["BankBranchIdentifier"] = supplier.get("BankAccNumber")
                else:
                    QuerySet9["BankBranchIdentifier"] = "111-111"

            if supplier.get("BankAccNumber") not in ["", None]:
                QuerySet9["BankAccountNumber"] = supplier.get("BankAccNumber")[6:16]
            else:
                QuerySet9["BankAccountNumber"] = "NA"

            if supplier.get("Details") not in ["", None]:
                QuerySet9["StatementText"] = supplier.get("Details")
            else:
                QuerySet9["StatementText"] = "NA"

            if QuerySet9["BankBranchIdentifier"] == None:
                QuerySet2["VendorPaymentBankDetail"] = None
            else:
                QuerySet2["VendorPaymentBankDetail"] = QuerySet9

            QuerySet2["VendorPaymentBankDetail"] = None
            payload = json.dumps(QuerySet2)

            post_data_in_qbo(url, headers, payload, supplier_data, _id, job_id, task_id, supplier.get("Name"))


    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_supplier -> add_xero_supplier", ex)
