import json
import logging

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database

import logging
from apps.util.qbo_util import post_data_in_qbo


def add_xero_archieved_customer(job_id, task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_customer -> add_xero_archived_customer")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)

        url = f"{base_url}/customer?minorversion={minorversion}"

        customer_data = dbname["xero_archived_customer"]
        customers = customer_data.find({"job_id": job_id})

        xero_invoice = dbname["xero_invoice"].find({"job_id": job_id})

        multiple_invoice = []
        for p1 in xero_invoice:
            multiple_invoice.append(p1)

        for customer in customers:
            _id = customer.get("_id")
            task_id = customer.get("task_id")
            QuerySet2 = {}
            QuerySet3 = {}
            QuerySet31 = {}
            QuerySet4 = {}
            QuerySet5 = {}
            QuerySet8 = {}
            QuerySet9 = {}
            WebAddr = {}

            customer_address = customer.get("Address")
            customer_phone = customer.get("Phone")

            if len(customer_address) != 0:
                if "AddressLine1" in customer_address[0]:
                    QuerySet3["Line1"] = customer_address[0].get("AddressLine1")
                if "AddressLine2" in customer_address[0]:
                    QuerySet3["Line2"] = customer_address[0].get("AddressLine2")
                if "City" in customer_address[0]:
                    QuerySet3["City"] = customer_address[0].get("City")
                if "PostalCode" in customer_address[0]:
                    QuerySet3["PostalCode"] = customer_address[0].get("PostalCode")
                if "Region" in customer_address[0]:
                    QuerySet3["CountrySubDivisionCode"] = customer_address[0].get(
                        "Region"
                    )
                if "Country" in customer_address[0]:
                    QuerySet3["Country"] = customer_address[0].get("Country")

                if "AddressLine1" in customer_address[1]:
                    QuerySet31["Line1"] = customer_address[1].get("AddressLine1")
                if "AddressLine2" in customer_address[1]:
                    QuerySet31["Line2"] = customer_address[1].get("AddressLine2")
                if "City" in customer_address[1]:
                    QuerySet31["City"] = customer_address[1].get("City")
                if "PostalCode" in customer_address[1]:
                    QuerySet31["PostalCode"] = customer_address[1].get("PostalCode")
                if "Region" in customer_address[1]:
                    QuerySet31["CountrySubDivisionCode"] = customer_address[1].get("Region")
                if "Country" in customer_address[1]:
                    QuerySet31["Country"] = customer_address[1].get("Country")

                if len(customer_phone) != 0:
                    QuerySet4["FreeFormNumber"] = customer_phone[1].get("PhoneNumber")[0:30] if customer_phone[1].get(
                        "PhoneNumber") == True else None
                    QuerySet8["FreeFormNumber"] = customer_phone[3].get("PhoneNumber")[0:30] if customer_phone[3].get(
                        "PhoneNumber") == True else None
                    QuerySet9["FreeFormNumber"] = customer_phone[2].get("PhoneNumber")[0:30] if customer_phone[2].get(
                        "PhoneNumber") == True else None

            QuerySet5["Address"] = customer.get("email")
            QuerySet2["BillAddr"] = QuerySet31
            QuerySet2["ShipAddr"] = QuerySet3
            QuerySet2["PrimaryPhone"] = QuerySet4
            QuerySet2["PrimaryEmailAddr"] = QuerySet5
            # if 'Website' in customer:
            #     if customer['Website'].startswith('http'):
            #         WebAddr['URI'] = customer.get('Website']
            #     else:
            #         WebAddr['URI'] = "https://" + customer['Website']

            # QuerySet2['WebAddr'] = WebAddr
            QuerySet2["Fax"] = QuerySet9
            QuerySet2["Mobile"] = QuerySet8
            QuerySet2["DisplayName"] = customer.get("Name").replace(":", "-")
            QuerySet2["GivenName"] = customer.get("FirstName")
            QuerySet2["FamilyName"] = customer.get("LastName")
            QuerySet2["PrimaryTaxIdentifier"] = customer.get("TaxNumber")
            payload = json.dumps(QuerySet2)

            post_data_in_qbo(url, headers, payload, dbname["xero_archived_customer"], _id, job_id, task_id,
                             customer.get('Name'))

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_customer -> add_xero_archived_customer", ex)
