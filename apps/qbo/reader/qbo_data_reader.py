import traceback

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.qbo_util import get_data_from_qbo


def read_qbo_data(job_id, task_id, read_data_from_object):
    configurations = []
    try:
        base_url, headers, company_id, minorversion, get_data_header, report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/query?minorversion={minorversion}"
        print(url)
        print(read_data_from_object)
        if read_data_from_object == "Invoice":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Invoice",
                                   "task_id": task_id,
                                   "json_object_key": "Invoice",
                                   "qbo_object_name": "Invoice",
                                   "url": url,
                                   "header": get_data_header})
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_CreditMemo",
                                   "task_id": task_id,
                                   "json_object_key": "CreditMemo",
                                   "qbo_object_name": "CreditMemo",
                                   "url": url,
                                   "header": get_data_header})
            
        if read_data_from_object == "Chart of Account" or read_data_from_object == "Chart of account":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_COA",
                                   "task_id": task_id,
                                   "json_object_key": "Account",
                                   "qbo_object_name": "Account",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Bill Payment":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Bill_Payment",
                                   "task_id": task_id,
                                   "json_object_key": "BillPayment",
                                   "qbo_object_name": "BillPayment",
                                   "url": url,
                                   "header": get_data_header})
            
        if read_data_from_object == "Invoice Payment":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Payment",
                                   "task_id": task_id,
                                   "json_object_key": "Payment",
                                   "qbo_object_name": "payment",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Bill":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Bill",
                                   "task_id": task_id,
                                   "json_object_key": "Bill",
                                   "qbo_object_name": "Bill",
                                   "url": url,
                                   "header": get_data_header})
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_VendorCredit",
                                   "task_id": task_id,
                                   "json_object_key": "VendorCredit",
                                   "qbo_object_name": "VendorCredit",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Bank Transfer":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Bank_Transfer",
                                   "task_id": task_id,
                                   "json_object_key": "Transfer",
                                   "qbo_object_name": "Transfer",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Customer":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Customer",
                                   "task_id": task_id,
                                   "json_object_key": "Customer",
                                   "qbo_object_name": "customer",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Department":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Department",
                                   "task_id": task_id,
                                   "json_object_key": "Department",
                                   "qbo_object_name": "department",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Employee":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Employee",
                                   "task_id": task_id,
                                   "json_object_key": "Employee",
                                   "qbo_object_name": "employee",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Item":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Item",
                                   "task_id": task_id,
                                   "json_object_key": "Item",
                                   "qbo_object_name": "item",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Job":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Class",
                                   "task_id": task_id,
                                   "json_object_key": "Class",
                                   "qbo_object_name": "Class",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Journal":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Journal",
                                   "task_id": task_id,
                                   "json_object_key": "JournalEntry",
                                   "qbo_object_name": "journalentry",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Receive Money":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Received_Money",
                                   "task_id": task_id,
                                   "json_object_key": "Deposit",
                                   "qbo_object_name": "deposit",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Spend Money":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Spend_Money",
                                   "task_id": task_id,
                                   "json_object_key": "Purchase",
                                   "qbo_object_name": "purchase",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Supplier":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Supplier",
                                   "task_id": task_id,
                                   "json_object_key": "Vendor",
                                   "qbo_object_name": "vendor",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Taxcode":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Taxcode",
                                   "task_id": task_id,
                                   "json_object_key": "TaxCode",
                                   "qbo_object_name": "taxcode",
                                   "url": url,
                                   "header": get_data_header})
        if read_data_from_object == "Taxrate":
            configurations.append({"job_id": job_id,
                                   "table_name": "QBO_Taxrate",
                                   "task_id": task_id,
                                   "json_object_key": "TaxRate",
                                   "qbo_object_name": "taxrate",
                                   "url": url,
                                   "header": get_data_header})
        for config in configurations:
            get_data_from_qbo(config.get("job_id"), config.get("task_id"), config.get("table_name"),
                              config.get("json_object_key"),
                              config.get("qbo_object_name"), config.get("url"), config.get("header"))
    
    except Exception as ex:
        traceback.print_exc()
        
