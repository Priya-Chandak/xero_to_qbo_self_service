from apps.home.data_util import update_task_execution_status, write_task_execution_step
from apps.myob.delete_apis import *
from apps.qbo.account.account_referrence import account_reference
from apps.qbo.account.add_xero_duplicate_chart_of_account import (
    add_xero_duplicate_chart_account, update_xero_existing_chart_account
)
from apps.qbo.reader.QBO_combined_tax import get_qbo_tax
from apps.qbo.reader.qbo_data_reader import read_qbo_data
from apps.qbo.reader.taxcode import get_qbo_taxcode
from apps.qbo.reader.taxrate import get_qbo_taxrate
from apps.xero.reader.customer_archived import get_xero_archived_customer
from apps.xero.reader.supplier_archived import get_xero_archived_supplier
from apps.xero.qbo_writer.add_bank_transfer import add_xero_bank_transfer
from apps.xero.qbo_writer.add_chart_of_account import add_xero_chart_account,add_xero_archived_chart_account
from apps.xero.qbo_writer.add_customer import add_xero_customer
from apps.xero.qbo_writer.add_archieved_customer import add_xero_archieved_customer,get_used_archived_customers
from apps.xero.qbo_writer.add_archieved_supplier import add_xero_archieved_supplier, get_used_archived_suppliers
from apps.xero.qbo_writer.add_employee import add_xero_employee
from apps.xero.qbo_writer.add_item import *
from apps.xero.qbo_writer.add_item_purchase_order import add_xero_item_purchase_order
from apps.xero.qbo_writer.add_item_quotes import add_xero_item_quote
from apps.xero.qbo_writer.add_item_using_invoice import create_item_from_xero_invoice_acccode_itemcode, \
    create_item_xero_invoice_accountcode, create_item_from_xero_creditnote_acccode_itemcode, create_item_xero_creditnote_accountcode, create_item_xero_bill_accountcode, create_item_from_xero_bill_acccode_itemcode
from apps.xero.qbo_writer.add_job import add_xero_job
from apps.xero.qbo_writer.add_journal import add_xero_journal
from apps.xero.qbo_writer.add_payment import add_xero_invoice_payment, add_xero_bill_payment, \
    add_xero_bill_payment_as_journal, add_xero_invoice_payment_as_journal,add_xero_supplier_credit_cash_refund_as_journal,add_xero_receive_overpayment_cash_refund_as_journal,add_xero_spend_overpayment_cash_refund_as_journal
from apps.xero.qbo_writer.add_receive_prepayment import add_receive_prepayment, add_receive_overpayment
from apps.xero.qbo_writer.add_received_money import add_xero_receive_money
from apps.xero.qbo_writer.add_credit_card_credit import add_xero_credit_card_credit
from apps.xero.qbo_writer.add_service_purchase_order import (
    add_service_xero_purchase_order,
)
from apps.xero.qbo_writer.add_receive_money_as_spend_money import add_xero_negative_received_money
from apps.xero.qbo_writer.add_spend_money_as_receive_money import add_xero_negative_spend_money_as_receive_money,add_xero_spend_money_as_credit_card_credit
from apps.xero.qbo_writer.add_spend_money import add_xero_spend_money
from apps.xero.myob_ledger_writer.add_archived_customer import add_xero_archived_customer_to_myobledger
from apps.xero.myob_ledger_writer.add_archived_supplier import add_xero_archived_supplier_to_myobledger
from apps.xero.qbo_writer.add_spend_prepayment import add_spend_overpayment, add_spend_prepayment
from apps.xero.qbo_writer.add_supplier import add_xero_supplier
from apps.xero.qbo_writer.get_qbo_invoice_for_payments import get_qbo_invoice_for_payments,get_qbo_bill_for_payments 
from apps.xero.qbo_writer.add_vendorcredit import add_vendorcredit
from apps.xero.qbo_writer.add_xero_credit_note import add_xero_credit_note
# from apps.xero.qbo_writer.add_xero_invoice_1 import add_xero_invoice
from apps.xero.qbo_writer.add_xero_invoice import add_xero_invoice
from apps.xero.qbo_writer.get_COA_classification import get_xero_classified_coa,get_xero_classified_archived_coa
from apps.xero.qbo_writer.test_combined_bill import add_xero_bill
from apps.xero.reader.bank_transfer import get_xero_bank_transfer
from apps.xero.reader.chart_of_account import get_coa, get_archieved_coa
from apps.xero.reader.classified_bill import get_classified_bill
from apps.xero.reader.customer import get_xero_customer
from apps.xero.reader.supplier import get_xero_supplier 
from apps.xero.reader.creditnote import get_creditnote
from apps.xero.reader.vendorcredit import get_vendorcredit
from apps.xero.reader.employee import get_xero_employee
from apps.xero.reader.invoice import get_invoice,get_invoice_customers
from apps.xero.reader.bill import get_xero_bill, get_bill_suppliers
from apps.xero.reader.items import get_items
from apps.xero.reader.job import get_xero_job
from apps.xero.reader.manual_journal import get_manual_journal
from apps.xero.reader.payment import get_xero_payment
from apps.xero.reader.purchase_order import get_xero_purchase_order
from apps.xero.reader.quotes import get_xero_quotes
from apps.xero.reader.spend_money import get_xero_spend_money
from apps.xero.reader.receive_money import get_xero_receive_money

from apps.xero.reader.tax import get_xero_tax
from apps.util.db_mongo import get_mongodb_database
from apps.myconstant import JOB_STATUS_IN_PROGRESS


class XeroToQbo(object):
    
    @staticmethod
    def read_data(job_id, task):
        step_name = None
        try:
            dbname = get_mongodb_database()

            if "Existing Chart of account" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading xero chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from xero classified coa"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_classified_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from xero tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo taxrate"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo chart of account"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")


            if "Chart of account" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading xero chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from xero classified coa"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_classified_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from xero tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo taxrate"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo chart of account"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Archieved Chart of account" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading xero chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_archieved_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from xero classified coa"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_classified_archived_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from xero tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo taxrate"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo chart of account"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")
                
            if "Job" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Xero Job data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_job(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Customer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Xero Customer data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_customer(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Archieved Customer" == task.function_name:
                update_task_execution_status( task.id, status=2, task_type="read")

                step_name = "Reading Invoice data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice_customers(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from Archieved Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_archived_customer(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Archieved Supplier" == task.function_name:
                update_task_execution_status( task.id, status=2, task_type="read")
                
                step_name = "Reading Invoice data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill_suppliers(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from Archieved Supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_archived_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")


            if "Employee" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Xero Employee data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_employee(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Supplier" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Xero Supplier data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Item" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Xero Item data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_items(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading xero chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo chart of account"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading account reference data "
                write_task_execution_step(task.id, status=2, step=step_name)
                account_reference(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Spend Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Xero Spend Money data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_spend_money(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading xero chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                results=dbname['xero_coa'].count_documents({"job_id":job_id})
                if results == 0:
                    get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo chart of data"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Supplier")
                write_task_execution_step(task.id, status=1, step=step_name)

                
                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo job"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Job")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Customer")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Receive Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Xero Receive Money data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_receive_money(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Reading xero chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                results=dbname['xero_coa'].count_documents({"job_id":job_id})
                if results == 0:
                    get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                step_name = "Reading qbo chart of data"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Supplier")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo job"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Job")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Employee"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Employee")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Customer")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")
                

            if "Journal" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Xero Journal data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_manual_journal(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading xero chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from qbo chart of account"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)


                update_task_execution_status(task.id, status=1, task_type="read")

            if "Invoice" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Invoice data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo chart of data"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Supplier")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo job"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Job")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Customer")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Invoice CreditNote" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading CreditNote data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_creditnote(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Reading qbo chart of data"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Supplier")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo job"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Job")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Customer")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")
            
            if "Bill" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading bill data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_bill(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo chart of data"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Supplier")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo job"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Job")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Customer")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading xero Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_items(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo COA"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Bill VendorCredit" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading VendorCredit data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_vendorcredit(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo chart of data"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Supplier")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo job"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Job")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Customer")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading xero Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_items(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo COA"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")
            
            if "Payment Allocation" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Payment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_payment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Invoice"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Invoice")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Bill"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Bill")
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Invoice Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Invoice Payment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_payment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_qbo_invoice_for_payments(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
   

                step_name = "Reading qbo chart of data"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Supplier")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Customer")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading Xero COA"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading Xero Archived COA"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_archieved_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
   
                update_task_execution_status(task.id, status=1, task_type="read")


            if "Bill Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Bill Payment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_payment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Bill"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_bill_for_payments(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo chart of data"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Supplier")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxcode"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo taxrate "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_taxrate(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_qbo_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Customer")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading Xero COA"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading Xero Archived COA"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_archieved_coa(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
               
                update_task_execution_status(task.id, status=1, task_type="read")

            
            if "Bank Transfer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Bank Transfer data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_bank_transfer(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Quotes" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Quotes data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_quotes(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Purchase Order" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading Purchase Order data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_xero_purchase_order(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")


        except Exception as ex:
            write_task_execution_step(
                job_id, task.id, status=0, step=step_name)
            update_task_execution_status(
                task.id, status=0, task_type="read")
            raise ex

    @staticmethod
    def write_data(job_id, task):
        step_name = None
        try:
            dbname = get_mongodb_database()

            if "Existing Chart of account" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Updating existing chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                update_xero_existing_chart_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Chart of account" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Duplicate chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_duplicate_chart_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_chart_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Archieved Chart of account" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_archived_chart_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")
            
            if "Job" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Job data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_job(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")

            if "Customer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Customer data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_customer(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")

            if "Archieved Customer" == task.function_name:
                update_task_execution_status( task.id, status=2, task_type="write")

                step_name = "Adding data Archieved Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_used_archived_customers(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Adding data Archieved Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_archieved_customer(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Archieved Supplier" == task.function_name:
                update_task_execution_status( task.id, status=2, task_type="write")
                
                step_name = "Adding data Archieved Customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_used_archived_suppliers(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Adding data Archieved Supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_archieved_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")


            if "Employee" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Employee data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_employee(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Supplier" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Supplier data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Item" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Adding duplicate item data "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_duplicate_item(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Adding Items data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_item(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading Invoice data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Create Item ItemCode From Invoice"
                write_task_execution_step(task.id, status=2, step=step_name)
                create_item_from_xero_invoice_acccode_itemcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Create Item AccountCode From Invoice"
                write_task_execution_step(task.id, status=2, step=step_name)
                create_item_xero_invoice_accountcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Create Item ItemCode From bill"
                write_task_execution_step(task.id, status=2, step=step_name)
                create_item_from_xero_bill_acccode_itemcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Create Item AccountCode From bill"
                write_task_execution_step(task.id, status=2, step=step_name)
                create_item_xero_bill_accountcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Reading Creditnotes data"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_creditnote(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Create Item ItemCode From CreditNote"
                write_task_execution_step(task.id, status=2, step=step_name)
                create_item_from_xero_creditnote_acccode_itemcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Create Item AccountCode From Invoice"
                write_task_execution_step(task.id, status=2, step=step_name)
                create_item_xero_creditnote_accountcode(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="write")

            if "Spend Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                
                step_name = "Add Positive Spend Money data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_spend_money(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Negative Spend Money As Receive Money"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_negative_spend_money_as_receive_money(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Add Negative Spend Money As CRC"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_spend_money_as_credit_card_credit(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Add Spend Money Prepayment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_spend_prepayment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Spend Money Overpayment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_spend_overpayment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Receive Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Positive Receive Money data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_receive_money(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Credit Card Credit Data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_credit_card_credit(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Negative Received Money data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_negative_received_money(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Add Receive Money Prepayment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_receive_prepayment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Receive Money Overpayment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_receive_overpayment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Journal" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Journal data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_journal(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Invoice" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Invoice data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_invoice(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Invoice CreditNote" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Credit Note data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_credit_note(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Bill" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Bill data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_bill(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Bill VendorCredit" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Vendor Credit data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_vendorcredit(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")
        
            
            if "Invoice Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")
                
                step_name = "Add Invoice Payment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_invoice_payment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Invoice Payment as Journal"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_invoice_payment_as_journal(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")


            if "Bill Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")
                
                step_name = "Add Bill Payment data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_bill_payment(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Bill Payment as Journal"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_bill_payment_as_journal(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add vendor Credit Cash Refund as Journal"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_supplier_credit_cash_refund_as_journal(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Receive Money Over Payment Cash Refund as Journal"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_receive_overpayment_cash_refund_as_journal(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Spend Money Over Payment Cash Refund as Journal"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_spend_overpayment_cash_refund_as_journal(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="write")


            if "Bank Transfer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Reading qbo chart of account"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Chart of account")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Bank Transfer"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_bank_transfer(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Quotes" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Quotes data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_item_quote(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Purchase Order" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Create Item from Purchase Order"
                write_task_execution_step(task.id, status=2, step=step_name)
                create_item_from_xero_purchase_order(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "delete item"
                write_task_execution_step(task.id, status=2, step=step_name)
                delete_item(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading qbo Item"
                write_task_execution_step(task.id, status=2, step=step_name)
                read_qbo_data(job_id,task.id, "Item")
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Item Purchase Order"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_xero_item_purchase_order(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Add Service Purchase Order"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_service_xero_purchase_order(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")


        except Exception as ex:
            write_task_execution_step(
                job_id, task.id, status=0, step=step_name)
            update_task_execution_status(
                task.id, status=0, task_type="write")
            raise ex
