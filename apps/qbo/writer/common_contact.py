import traceback

from apps.home.data_util import add_job_status
from apps.util.db_mongo import get_mongodb_database


def get_common_contact(job_id):
    try:
        db = get_mongodb_database()
        supplier_data = db["supplier"]
        customer_data = db["customer"]
        supplier = supplier_data.find({"job_id":job_id})
        customer = customer_data.find({"job_id":job_id})
        cust1 = []
        for k1 in customer:
            cust1.append(k1)
        supp1 = []
        for k2 in supplier:
            supp1.append(k2)
        customer1 = []
        for i in range(0, len(cust1)):
            if "CompanyName" in cust1[i]:
                customer1.append(cust1[i]["CompanyName"])
            else:
                customer1.append(cust1[i]["FirstName"] + " " + cust1[i]["LastName"])
        supplier1 = []
        for i in range(0, len(supp1)):
            if "Company_Name" in supp1[i]:
                supplier1.append(supp1[i]["Company_Name"])
            else:
                customer1.append(supp1[i]["First_Name"] + " " + supp1[i]["Last_Name"])
        common_contact = []
        customer_set = set(customer1)
        supplier_set = set(supplier1)
        if customer_set & supplier_set:
            common_contact.append((customer_set & supplier_set))
        else:
            pass
        common_contact1 = list(common_contact[0])
    except Exception as ex:
        traceback.print_exc()
        
