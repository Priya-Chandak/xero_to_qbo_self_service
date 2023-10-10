import json
import logging

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo

logger = logging.getLogger(__name__)


def add_xero_job(job_id, task_id):
    try:
        logger.info("Started executing xero -> qbowriter -> add_job -> add_xero_job")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/class?minorversion={minorversion}"
        xero_job1 = dbname["xero_job"]

        x = xero_job1.find({"job_id": job_id})
        data1 = []
        for k in x:
            data1.append(k)

        QuerySet1 = data1

        for i in range(0, len(QuerySet1)):
            _id = QuerySet1[i]["_id"]
            task_id = QuerySet1[i]['task_id']
            QuerySet2 = {}

            QuerySet2["Name"] = QuerySet1[i]["Name"]

            payload = json.dumps(QuerySet2)

            post_data_in_qbo(url, headers, payload, dbname["xero_job"], _id, job_id, task_id, QuerySet1[i]["Name"])


    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_job -> add_xero_job", ex)
