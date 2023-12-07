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
from apps.xero.qbo_writer.add_customer import add_xero_customer, add_default_xero_customer
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
from apps.xero.qbo_writer.add_open_payment import add_open_xero_bill_payment,add_open_xero_invoice_payment,add_xero_open_receive_overpayment_cash_refund_as_journal,add_xero_open_spend_overpayment_cash_refund_as_journal
from apps.xero.qbo_writer.add_payment import add_xero_invoice_payment, add_xero_bill_payment, \
    add_xero_bill_payment_as_journal, add_xero_invoice_payment_as_journal,add_xero_supplier_credit_cash_refund_as_journal,add_xero_receive_overpayment_cash_refund_as_journal,add_xero_spend_overpayment_cash_refund_as_journal,add_xero_creditnote_payment_refund_as_journal
from apps.xero.qbo_writer.add_receive_prepayment import add_receive_prepayment, add_receive_overpayment
from apps.xero.qbo_writer.add_received_money import add_xero_receive_money
from apps.xero.qbo_writer.add_open_spend_overpayment import add_open_spend_overpayment, add_open_receive_overpayment
from apps.xero.qbo_writer.add_credit_card_credit import add_xero_credit_card_credit
from apps.xero.qbo_writer.add_service_purchase_order import (
    add_service_xero_purchase_order,
)
from apps.xero.qbo_writer.add_receive_money_as_spend_money import add_xero_negative_received_money
from apps.xero.qbo_writer.add_spend_money_as_receive_money import add_xero_negative_spend_money_as_receive_money,add_xero_spend_money_as_credit_card_credit
from apps.xero.qbo_writer.add_spend_money import add_xero_spend_money
from apps.xero.qbo_writer.add_spend_prepayment import add_spend_overpayment, add_spend_prepayment
from apps.xero.qbo_writer.add_supplier import add_xero_supplier, add_default_xero_supplier
from apps.xero.qbo_writer.get_qbo_invoice_for_payments import get_qbo_invoice_for_payments,get_qbo_bill_for_payments 
from apps.xero.qbo_writer.add_vendorcredit import add_vendorcredit
from apps.xero.qbo_writer.add_open_vendorcredit import add_open_xero_vendorcredit,add_xero_open_supplier_credit_cash_refund_as_journal
from apps.xero.qbo_writer.add_xero_credit_note import add_xero_credit_note,add_xero_open_credit_memo_cash_refund_as_journal
# from apps.xero.qbo_writer.add_xero_invoice_1 import add_xero_invoice
from apps.xero.qbo_writer.add_xero_invoice import add_xero_invoice
from apps.xero.qbo_writer.add_xero_open_invoice import add_xero_open_invoice
from apps.xero.qbo_writer.add_xero_open_credit_note import add_xero_open_credit_note
from apps.xero.qbo_writer.get_COA_classification import get_xero_classified_coa,get_xero_classified_archived_coa
from apps.xero.qbo_writer.add_xero_bill import add_xero_bill
from apps.xero.qbo_writer.add_xero_open_bill import add_xero_open_bill
from apps.xero.reader.bank_transfer import get_xero_bank_transfer
from apps.xero.reader.chart_of_account import get_coa, get_archieved_coa
from apps.xero.reader.classified_bill import get_classified_bill
from apps.xero.reader.customer import get_xero_customer
from apps.xero.reader.supplier import get_xero_supplier 
from apps.xero.reader.creditnote import get_creditnote,get_open_creditnote
from apps.xero.reader.vendorcredit import get_vendorcredit
from apps.xero.reader.employee import get_xero_employee
from apps.xero.reader.payrun import get_payrun,get_payslip,get_payrun_setting
from apps.xero.reader.depreciation import *
from apps.xero.reader.add_payrun import add_xero_payrun
from apps.xero.reader.invoice import get_invoice,get_invoice_customers,get_open_invoice
from apps.xero.reader.AR_Summary import get_aged_receivable_summary, get_aged_payable_summary,get_qbo_ar_customer,get_qbo_ap_supplier, get_qbo_trial_balance, get_xero_trial_balance,match_trial_balance,get_xero_current_trial_balance,get_qbo_current_trial_balance_after_conversion
from apps.xero.reader.AR_Journal import add_qbo_ar_journal, add_qbo_ap_journal, add_qbo_reverse_trial_balance, add_xero_open_trial_balance,add_xero_current_trial_balance
from apps.xero.reader.bill import get_xero_bill, get_bill_suppliers
from apps.xero.reader.items import get_items
from apps.xero.reader.job import get_xero_job
from apps.xero.reader.manual_journal import get_manual_journal
from apps.xero.reader.payment import get_xero_payment, get_open_xero_payment
from apps.xero.reader.open_spend_overpayment import get_xero_open_overpayment
from apps.xero.reader.purchase_order import get_xero_purchase_order
from apps.xero.reader.quotes import get_xero_quotes
from apps.xero.reader.spend_money import get_xero_spend_money
from apps.xero.reader.receive_money import get_xero_receive_money

from apps.xero.reader.tax import get_xero_tax
from apps.util.db_mongo import get_mongodb_database
from apps.myconstant import JOB_STATUS_IN_PROGRESS



class XeroToQboReports(object):
    @staticmethod
    def read_data(job_id, task):
        step_name = None
        try:
            dbname = get_mongodb_database()
            
            update_task_execution_status(task.id, status=2, task_type="read")

            step_name = "Reading xero open invoices"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_open_invoice(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading xero open CR"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_open_creditnote(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading xero open CR"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_open_xero_payment(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading xero open Receive Over payment"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_xero_open_overpayment(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading xero open Aged Receivable Summary"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_aged_receivable_summary(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading xero open Aged Payable Summary"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_aged_payable_summary(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            delete_supplier(job_id,task.id)
            delete_customer(job_id,task.id)
            delete_coa(job_id,task.id)
            
            step_name = "Add default customer to QBO"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_default_xero_customer(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Add default supplier to QBO"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_default_xero_supplier(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading qbo chart of data"
            write_task_execution_step(task.id, status=2, step=step_name)
            read_qbo_data(job_id,task.id, "Chart of account")
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading qbo Customer"
            write_task_execution_step(task.id, status=2, step=step_name)
            read_qbo_data(job_id,task.id, "Customer")
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo supplier"
            write_task_execution_step(task.id, status=2, step=step_name)
            read_qbo_data(job_id,task.id, "Supplier")
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Create Item ItemCode From Invoice"
            write_task_execution_step(task.id, status=2, step=step_name)
            create_item_from_xero_invoice_acccode_itemcode(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Create Item AccountCode From Invoice"
            write_task_execution_step(task.id, status=2, step=step_name)
            create_item_xero_invoice_accountcode(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo Item"
            write_task_execution_step(task.id, status=2, step=step_name)
            delete_item(job_id,task.id)
            read_qbo_data(job_id,task.id, "Item")
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading xero open invoices"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_open_invoice(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Open Credit Note data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_open_credit_note(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading qbo Invoice"
            write_task_execution_step(
                task.id, status=2, step=step_name)
            get_qbo_invoice_for_payments(job_id,task.id)
            write_task_execution_step(
                task.id, status=1, step=step_name)

            step_name = "Reading Xero COA"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_coa(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Reading Xero Archived COA"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_archieved_coa(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Invoice Payment data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_open_xero_invoice_payment(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add xero open bill"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_open_bill(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            delete_bill(job_id)
            step_name = "Reading qbo Bill"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_qbo_bill_for_payments(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Bill Payment data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_open_xero_bill_payment(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Vendor Credit data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_open_xero_vendorcredit(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Add Spend Money Overpayment data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_open_spend_overpayment(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Receive Money Overpayment data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_open_receive_overpayment(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Open Supplier Credit Cash Refund data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_open_supplier_credit_cash_refund_as_journal(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Open Supplier Credit Cash Refund data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_open_credit_memo_cash_refund_as_journal(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Open Receive Overpayment Cash Refund data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_open_receive_overpayment_cash_refund_as_journal(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)

            step_name = "Add Open Spend Overpayment Cash Refund data"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_open_spend_overpayment_cash_refund_as_journal(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo AR Customer"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_qbo_ar_customer(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo AP Supplier"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_qbo_ap_supplier(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo AR Customer"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_qbo_ar_journal(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo AR Customer"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_qbo_ap_journal(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading QBO Trial Balance"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_qbo_trial_balance(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo AR Customer"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_qbo_reverse_trial_balance(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading xero trial balance"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_xero_trial_balance(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo AR Customer"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_open_trial_balance(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading xero trial balance"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_xero_current_trial_balance(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading QBO Trial Balance of today's date"
            write_task_execution_step(task.id, status=2, step=step_name)
            get_qbo_current_trial_balance_after_conversion(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading xero trial balance"
            write_task_execution_step(task.id, status=2, step=step_name)
            match_trial_balance(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            step_name = "Reading qbo AR Customer"
            write_task_execution_step(task.id, status=2, step=step_name)
            add_xero_current_trial_balance(job_id,task.id)
            write_task_execution_step(task.id, status=1, step=step_name)
            
            
            update_task_execution_status(task.id, status=1, task_type="read")


        except Exception as ex:
            write_task_execution_step(
                job_id, task.id, status=0, step=step_name)
            update_task_execution_status(
                task.id, status=0, task_type="read")
            raise ex

    