import asyncio
import json

from apps.mmc_settings.all_settings import get_settings_myob
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob


def add_xero_job_to_myobledger(job_id, task_id):
    try:
        db = get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload = {}

        job1 = db['xero_job']

        x = job1.find({"job_id": job_id})
        data1 = []
        for k in x:
            data1.append(k)

        QuerySet1 = data1

        for i in range(0, len(QuerySet1)):
            _id = QuerySet1[i]['_id']
            task_id = QuerySet1[i]['task_id']
            QuerySet2 = {}

            # TrackingCategoryID or TrackingOptionID
            if "UID" in QuerySet1[i]:
                QuerySet2["Number"] = QuerySet1[i]["UID"][-4:]
                QuerySet2["Name"] = QuerySet1[i]["Name"][:30]
                QuerySet2["IsHeader"] = False

            payload = json.dumps(QuerySet2)
            id_or_name_value_for_error = (
                QuerySet1[i]["Name"]
                if QuerySet1[i]["Name"] is not None
                else "")

            payload1, base_url, headers = get_settings_myob(job_id)
            url = f"{base_url}/GeneralLedger/Job"

            if QuerySet1[i]['is_pushed'] == 0:
                asyncio.run(
                    post_data_in_myob(url, headers, payload, job1, _id, job_id, task_id, id_or_name_value_for_error))
            else:
                pass



    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
