import json
import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_job(job_id, task_id):
    try:
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        db = get_mongodb_database()
        url = f"{base_url}/class?minorversion={minorversion}"

        Collection = db["job"]

        QuerySet1 = list(Collection.find({"job_id": job_id}))

        for query in QuerySet1:
            _id = query['_id']
            task_id = query['task_id']
            QuerySet2 = {"Name": query["Name"] + "-" + query["Number"]}
            post_data_in_qbo(
                url,
                headers,
                json.dumps(QuerySet2),
                Collection,
                _id,
                job_id,
                task_id,
                query["Name"] if QuerySet2["Name"] is not None else ""
            )
    except Exception as ex:
        traceback.print_exc()
