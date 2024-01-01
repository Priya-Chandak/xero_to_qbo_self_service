import json
import logging

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo

import logging


def add_xero_employee(job_id, task_id):
    try:
        logging.info("Started executing xero -> qbowriter -> add_employee -> add_xero_employee")

        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/employee?minorversion={minorversion}"

        employee_data = db["xero_employee"]

        x = employee_data.find({"job_id": job_id})

        data = []
        for k in x:
            data.append(k)

        QuerySet1 = data

        for i in range(0, len(QuerySet1)):
            _id = QuerySet1['_id']
            task_id = QuerySet1['task_id']

            QuerySet2 = {}
            QuerySet4 = {}
            QuerySet5 = {}
            QuerySet6 = {}

            QuerySet2["EmployeeNumber"] = QuerySet1[i]["EmployeeID"]
            QuerySet2["SSN"] = QuerySet1[i]["EmployeeID"]
            QuerySet2["HiredDate"] = QuerySet1[i]["StartDate"]
            QuerySet2["BirthDate"] = QuerySet1[i]["DateOfBirth"]

            if QuerySet1[i]["Gender"] == "M":
                QuerySet2["Gender"] = "Male"
            elif QuerySet1[i]["Gender"] == "F":
                QuerySet2["Gender"] = "Female"
            else:
                pass

            QuerySet2["GivenName"] = QuerySet1[i]["FirstName"]
            QuerySet2["FamilyName"] = QuerySet1[i]["LastName"]
            QuerySet4["FreeFormNumber"] = QuerySet1[i]["Phone"]
            QuerySet5["Address"] = QuerySet1[i]["Email"]
            QuerySet6["FreeFormNumber"] = QuerySet1[i]["Mobile"]

            QuerySet2["PrimaryPhone"] = QuerySet4
            QuerySet2["PrimaryEmailAddr"] = QuerySet5
            QuerySet2["Mobile"] = QuerySet6

            payload = json.dumps(QuerySet2)

            post_data_in_qbo(url, headers, payload, employee_data, _id, job_id, task_id, QuerySet1[i]["EmployeeID"])


    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_employee -> add_xero_employee", ex)
