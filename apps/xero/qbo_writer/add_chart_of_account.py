import json
from apps.util.log_file import log_config
import logging

from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo

from apps.util.log_file import log_config
import logging


def add_xero_chart_account(job_id, task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_chart_of_account -> add_xero_chart_account")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/account?minorversion={minorversion}"

        classified_coa = dbname["xero_classified_coa"]
        x = classified_coa.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        QuerySet1 = data

        for j in range(0, len(QuerySet1)):
            try:
                _id = QuerySet1[j]['_id']
                task_id = QuerySet1[j]['task_id']

                QuerySet1[j].pop("job_id")
                QuerySet1[j].pop("is_pushed")
                QuerySet1[j].pop("_id")
                QuerySet1[j].pop("error")
                QuerySet1[j].pop("table_name")
                QuerySet1[j].pop("task_id")
                payload = json.dumps(QuerySet1[j])
                print(payload)
                post_data_in_qbo(url, headers, payload, dbname["xero_classified_coa"], _id, job_id, task_id,
                                 QuerySet1[j]["Name"])

            except Exception as ex:
                logging.error(ex, exc_info=True)
               

    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_chart_of_account -> add_xero_chart_account", ex)


def add_xero_archived_chart_account(job_id, task_id):
    log_config1=log_config(job_id)
    try:
        logging.info("Started executing xero -> qbowriter -> add_chart_of_account -> add_xero_chart_account")

        dbname = get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/account?minorversion={minorversion}"

        classified_coa = dbname["xero_classified_archived_coa"]
        x = classified_coa.find({"job_id": job_id})
        data = []
        for i in x:
            data.append(i)

        QuerySet1 = data

        for j in range(0, len(QuerySet1)):
            try:
                _id = QuerySet1[j]['_id']
                task_id = QuerySet1[j]['task_id']

                QuerySet1[j].pop("job_id")
                QuerySet1[j].pop("is_pushed")
                QuerySet1[j].pop("_id")
                QuerySet1[j].pop("error")
                QuerySet1[j].pop("table_name")
                QuerySet1[j].pop("task_id")
                payload = json.dumps(QuerySet1[j])
                print(payload)
                post_data_in_qbo(url, headers, payload, dbname["xero_classified_archived_coa"], _id, job_id, task_id,
                                 QuerySet1[j]["Name"])

            except Exception as ex:
                logging.error(ex, exc_info=True)
               
    except Exception as ex:
        logging.error(ex, exc_info=True)
        