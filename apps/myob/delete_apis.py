from apps.util.db_mongo import get_mongodb_database


def delete_coa(job_id,task_id):
    dbname = get_mongodb_database()
    dbname["QBO_COA"].delete_many({'job_id':job_id})


def delete_item(job_id,task_id):
    dbname = get_mongodb_database()
    dbname["QBO_Item"].delete_many({'job_id':job_id})


def delete_chart_of_account(job_id,task_id):
    dbname = get_mongodb_database()
    dbname["chart_of_account"].drop()

def delete_excel_reckon_invoice(job_id,task_id):
    dbname = get_mongodb_database()
    dbname["excel_reckon_invoice"].delete_many({'job_id':job_id})
    print("deleted-----------")

def delete_reckon_item(job_id,task_id):
    dbname = get_mongodb_database()
    dbname["reckon_item"].delete_many({'job_id':job_id})
    print("deleted-----------")

def delete_excel_reckon_bill(job_id,task_id):
    dbname = get_mongodb_database()
    dbname["excel_reckon_bill"].delete_many({'job_id':job_id})
    print("deleted-----------")
