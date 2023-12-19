from apps.home.data_util import update_task_execution_status, write_task_execution_step

from apps.xero.reader.open_spend_overpayment import get_xero_open_overpayment
from apps.util.db_mongo import get_mongodb_database
from apps.myconstant import *
from apps.qbo.reader.qbo_data_reader import read_qbo_data
from apps.myob.delete_apis import *
from apps.xero.reader.AR_Summary import get_aged_receivable_summary, get_aged_payable_summary,get_qbo_ar_customer,get_qbo_ap_supplier, get_xero_trial_balance,match_trial_balance,get_xero_current_trial_balance,get_qbo_current_trial_balance_before_conversion,get_qbo_current_trial_balance_after_conversion, get_aged_payable_summary_till_end_date,get_aged_receivable_summary_till_end_date, get_qbo_ar_customer_till_date,get_qbo_ap_supplier_till_end_date,trial_balance_final_report,get_qbo_trial_balance


class XeroToQboReports(object):
    @staticmethod
    def read_data(job_id,task):
        step_name = None
        try:
            dbname = get_mongodb_database()
            
            delete_customer(job_id)
            delete_supplier(job_id)
            
            step_name = "Reading qbo Customer"
            write_task_execution_step(task.id, status=2, step=step_name)
            read_qbo_data(job_id,task.id, "Customer")
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo supplier"
            write_task_execution_step(task.id, status=2, step=step_name)
            read_qbo_data(job_id,task.id, "Supplier")
            write_task_execution_step(task.id, status=1, step=step_name)
            
            delete_xero_ar(job_id)
            delete_xero_ap(job_id)

            step_name = "Reading xero open Aged Receivable Summary"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_aged_receivable_summary_till_end_date(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading xero open Aged Payable Summary"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_aged_payable_summary_till_end_date(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
                
        except Exception as ex:
            write_task_execution_step(
                job_id, status=0, step=step_name)
            raise ex
