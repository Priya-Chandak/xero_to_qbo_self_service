import json
import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_employee(job_id,task_id):
    try:
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        url = f"{base_url}/employee?minorversion={minorversion}"
        Collection = db["employee"]
        x = Collection.find({"job_id":job_id})

        QuerySet1 = []
        for i in x:
            QuerySet1.append(i)

        QuerySet1=QuerySet1
        for i in range(0, len(QuerySet1)):
            _id=QuerySet1[i]['_id']
            task_id=QuerySet1[i]['task_id']
            
            QuerySet2 = {"EmployeeNumber": QuerySet1[i]["Employee_ID_Number"], "SSN": QuerySet1[i]["Employee_ID"],
                         "HiredDate": QuerySet1[i]["Start_Date"], "ReleasedDate": QuerySet1[i]["End_Date"],
                         "BirthDate": QuerySet1[i]["Birth_Date"], "Gender": QuerySet1[i]["Gender"],
                         "BillRate": QuerySet1[i]["Cost_Per_Hour"], "BillableTime": True,
                         "GivenName": QuerySet1[i]["FirstName"], "FamilyName": QuerySet1[i]["LastName"],
                         "PrimaryAddr": {"Id": QuerySet1[i]["Addresses"][0]["Location"],
                                         "Line1": QuerySet1[i]["Addresses"][0]["Street"],
                                         "Line2": QuerySet1[i]["Addresses"][0]["Street"],
                                         "City": QuerySet1[i]["Addresses"][0]["City"],
                                         "Country": QuerySet1[i]["Addresses"][0]["Country"],
                                         "CountrySubDivisionCode": QuerySet1[i]["Addresses"][0]["State"],
                                         "PostalCode": QuerySet1[i]["Addresses"][0]["PostCode"]},
                         "PrimaryPhone": {"FreeFormNumber": QuerySet1[i]["Addresses"][0]["Phone2"]},
                         "PrimaryEmailAddr": {"Address": QuerySet1[i]["Addresses"][0]["Email"]},
                         "Mobile": {"FreeFormNumber": QuerySet1[i]["Addresses"][0]["Phone1"]}}
            
            print(json.dumps(QuerySet2))
            post_data_in_qbo(
                url,
                headers,
                json.dumps(QuerySet2),
                Collection,
                _id,
                job_id,
                task_id,
                f'{QuerySet1[i]["FirstName"]} {QuerySet1[i]["LastName"]}'
            )
    except Exception as ex:
        traceback.print_exc()
        
