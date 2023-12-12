from apps.util.db_mongo import get_mongodb_database
import redis

def delete_coa(job_id):
    dbname = get_mongodb_database()
    print(dbname["QBO_COA"].count_documents({'job_id': f"{job_id}"}))
    dbname["QBO_COA"].delete_many({'job_id': f"{job_id}"})
    print(dbname["QBO_COA"].count_documents({'job_id': f"{job_id}"}))
    print("deleted QBO COA")
    
def delete_xero_coa(job_id):
    dbname = get_mongodb_database()
    dbname["xero_coa"].delete_many({'job_id': f"{job_id}"})
     
def delete_xero_classified_coa(job_id):
    dbname = get_mongodb_database()
    dbname["xero_classified_coa"].delete_many({'job_id': f"{job_id}"})

def delete_item(job_id):
    
    dbname = get_mongodb_database()
    dbname["QBO_Item"].delete_many({'job_id': f"{job_id}"})

def delete_invoice(job_id):
    
    dbname = get_mongodb_database()
    dbname["QBO_Invoice"].delete_many({'job_id': f"{job_id}"})

def delete_creditnote(job_id):
    
    dbname = get_mongodb_database()
    dbname["QBO_CreditNote"].delete_many({'job_id': f"{job_id}"})

def delete_bill(job_id):
    
    dbname = get_mongodb_database()
    dbname["QBO_Bill"].delete_many({'job_id': f"{job_id}"})

def delete_customer(job_id):
    
    dbname = get_mongodb_database()
    dbname["QBO_Customer"].delete_many({'job_id': f"{job_id}"})

def delete_supplier(job_id):
    
    dbname = get_mongodb_database()
    dbname["QBO_Supplier"].delete_many({'job_id': f"{job_id}"})

def delete_chart_of_account(job_id):
    
    dbname = get_mongodb_database()
    dbname["chart_of_account"].drop()

def delete_excel_reckon_invoice(job_id):
    
    dbname = get_mongodb_database()
    dbname["excel_reckon_invoice"].delete_many({'job_id': f"{job_id}"})
    print("deleted-----------")


def delete_reckon_item(job_id):
    dbname = get_mongodb_database()
    dbname["reckon_item"].delete_many({'job_id': f"{job_id}"})
    print("deleted-----------")


def delete_excel_reckon_bill(job_id):
    dbname = get_mongodb_database()
    dbname["excel_reckon_bill"].delete_many({'job_id': f"{job_id}"})
    print("deleted-----------")

def delete_xero_ar(job_id):
    dbname=get_mongodb_database()
    dbname['xero_AR_till_end_date'].delete_many({'job_id': f"{job_id}"})
    print("deleted-----------")

def delete_xero_ap(job_id):
    dbname=get_mongodb_database()
    dbname['xero_AP_till_end_date'].delete_many({'job_id': f"{job_id}"})
    print("deleted-----------")