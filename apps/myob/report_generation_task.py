from apps.home.data_util import update_task_execution_status, write_task_execution_step

from apps.xero.reader.open_spend_overpayment import get_xero_open_overpayment
from apps.util.db_mongo import get_mongodb_database
from apps.myconstant import *


class XeroToQboReports(object):
    @staticmethod
    def read_data(job_id):
        step_name = None
        try:
            dbname = get_mongodb_database()

            # step_name = "Reading xero open Receive Over payment"
            # write_task_execution_step(job_id, status=2, step=step_name)
            # get_xero_open_overpayment(job_id)
            # write_task_execution_step(job_id, status=1, step=step_name)

        except Exception as ex:
            write_task_execution_step(
                job_id, status=0, step=step_name)
            raise ex
