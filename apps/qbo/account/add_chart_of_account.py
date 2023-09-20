import json
import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_chart_account(job_id,task_id):
    try:
        db = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/account?minorversion={minorversion}"
        classified_coa1 = db["classified_coa"]
        x = classified_coa1.find({"job_id":job_id})
        QuerySet1 = []
        for i in x:
            QuerySet1.append(i)

        QuerySet1=QuerySet1
        for j in range(0, len(QuerySet1)):
            try:
                _id=QuerySet1[j]['_id']
                task_id=QuerySet1[j]['task_id']
                QuerySet1[j].pop("job_id")
                QuerySet1[j].pop("is_pushed")
                QuerySet1[j].pop("_id")
                QuerySet1[j].pop("error")
                QuerySet1[j].pop("table_name")

                QuerySet1[j].pop("task_id")
                payload = json.dumps(QuerySet1[j])
                
                post_data_in_qbo(url, headers, payload,classified_coa1,_id, job_id,task_id, QuerySet1[j]["Name"])
            except Exception as ex:
                pass

    except Exception as ex:
        traceback.print_exc()
        
