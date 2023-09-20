from math import expm1
import requests
import json
from apps.home.data_util import add_job_status
from apps.home.models import Jobs, JobExecutionStatus
from apps.mmc_settings.all_settings import get_settings_qbo
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_qbo


def add_customer(job_id,task_id):
    
    try:
        db=get_mongodb_database()
        base_url, headers, company_id, minorversion, get_data_header,report_headers = get_settings_qbo(job_id)
        url = f"{base_url}/customer?minorversion={minorversion}"

        supplier_data = db['supplier']
        customer_data = db['customer']
        
        supplier = supplier_data.find({'job_id':job_id})
        customer = customer_data.find({'job_id':job_id})

        cust1 = []
        for k1 in customer:
            cust1.append(k1)
        
        supp1 = []
        for k2 in supplier:
            supp1.append(k2)

        supplier1=[]
        
        for i in range(0,len(supp1)):
            if 'CompanyName' in supp1[i] and supp1[i]['CompanyName']!=None :
                supplier1.append(supp1[i]['CompanyName'].replace(":","-"))
            elif 'FirstName' in supp1[i] and 'LastName' in supp1[i]:
                if supp1[i]['FirstName']!=None and supp1[i]['LastName']!=None:
                    supplier1.append(supp1[i]['FirstName'].replace(":","-")+" "+supp1[i]['LastName'].replace(":","-"))
        

        customer1=[]
        for i in range(0,len(cust1)):
            if 'Company_Name' in cust1[i] and cust1[i]['Company_Name']!=None:
                customer1.append(cust1[i]['Company_Name'].replace(":","-"))
            elif 'First_Name' in cust1[i] and 'Last_Name' in cust1[i]:
                if cust1[i]['First_Name']!=None and cust1[i]['Last_Name']!=None:
                    customer1.append(cust1[i]['First_Name'].replace(":","-")+" "+cust1[i]['Last_Name'].replace(":","-"))
        
        common_contact=[]
        customer_set = set(customer1)
        supplier_set = set(supplier1)

        if (customer_set & supplier_set):
            common_contact.append((customer_set & supplier_set))
        else:
            print("No common elements")

        if len(common_contact)>0:
            common_contact1=list(common_contact[0])
            # common_contact1=[]
            print(common_contact1)
       
        QuerySet1=cust1
        for i in range(0, len(QuerySet1)):
            _id=QuerySet1[i]['_id']
            task_id=QuerySet1[i]['task_id']
            
            QuerySet2 = {}
            QuerySet3 = {}
            QuerySet4 = {}
            QuerySet5 = {}
            QuerySet7 = {}
            QuerySet8 = {}
            QuerySet9 = {}

            QuerySet2['Notes'] = QuerySet1[i]['Notes']
            if len(common_contact)>0:
                if QuerySet1[i]['Company_Name'] != None:
                    if QuerySet1[i]['Company_Name'] in common_contact1:
                        QuerySet2['DisplayName'] = QuerySet1[i]['Company_Name'].replace(":","-") + "-C"
                    else:
                        QuerySet2['DisplayName'] = QuerySet1[i]['Company_Name'].replace(":","-")

                elif ('FirstName' in QuerySet1[i]) and ('LastName' in QuerySet1[i]) and (QuerySet1[i]['FirstName']!=None and QuerySet1[i]['LastName']!=None):
                    if QuerySet1[i]['Company_Name'] in common_contact1:
                        QuerySet2['DisplayName'] = QuerySet1[i]['FirstName'].replace(":","-") + " " + QuerySet1[i]['LastName'].replace(":","-")+ "-C"
                    else:
                        QuerySet2['DisplayName'] = QuerySet1[i]['FirstName'].replace(":","-") + " " + QuerySet1[i]['LastName'].replace(":","-")

            else:
                if QuerySet1[i]['Company_Name'] != None:
                    QuerySet2['DisplayName'] = QuerySet1[i]['Company_Name'].replace(":","-")
                elif ('FirstName' in QuerySet1[i]) and ('LastName' in QuerySet1[i]) and (QuerySet1[i]['FirstName']!=None and QuerySet1[i]['LastName']!=None):
                    QuerySet2['DisplayName'] = QuerySet1[i]['FirstName'].replace(":","-") + " " + QuerySet1[i]['LastName'].replace(":","-")
                
            if QuerySet1[i]['Addresses'] != None:
                QuerySet3['Line1'] = QuerySet1[i]['Addresses'][0]['Street']
                QuerySet3['City'] = QuerySet1[i]['Addresses'][0]['City']
                QuerySet3['Country'] = QuerySet1[i]['Addresses'][0]['Country']
                QuerySet3['CountrySubDivisionCode'] = QuerySet1[i]['Addresses'][0]['State']
                QuerySet3['PostalCode'] = QuerySet1[i]['Addresses'][0]['PostCode']
                QuerySet4['FreeFormNumber'] = QuerySet1[i]['Addresses'][0]['Phone1']
                QuerySet8['FreeFormNumber'] = QuerySet1[i]['Addresses'][0]['Fax']
                QuerySet9['FreeFormNumber'] = QuerySet1[i]['Addresses'][0]['Phone2']
                if 'Email' in QuerySet1[i]['Addresses'][0] and QuerySet1[i]['Addresses'][0]['Email']!=None: 
                    QuerySet5['Address'] = QuerySet1[i]['Addresses'][0]['Email'].strip()
                                
                # if QuerySet1[i]['Addresses'][0]['Website'] != None:
                #     QuerySet7['URI'] = "https://" + QuerySet1[i]['Addresses'][0]['Website']
                # else:
                #     QuerySet7['URI'] = None

            else:
                QuerySet3['Line1'] = None
                QuerySet3['City'] = None
                QuerySet3['Country'] = None
                QuerySet3['CountrySubDivisionCode'] = None
                QuerySet3['PostalCode'] = None
                QuerySet4['FreeFormNumber'] = None
                QuerySet8['FreeFormNumber'] = None
                QuerySet9['FreeFormNumber'] = None
                QuerySet5['Address'] = None
                QuerySet7['URI'] = None

            QuerySet2['WebAddr'] = QuerySet7
            QuerySet2['BillAddr'] = QuerySet3
            QuerySet2['PrimaryPhone'] = QuerySet4
            QuerySet2['PrimaryEmailAddr'] = QuerySet5
            QuerySet2['Fax'] = QuerySet8
            QuerySet2['AlternatePhone'] = QuerySet9
            payload = json.dumps(QuerySet2)
            print(payload)
           
            post_data_in_qbo(url, headers, payload,customer_data,_id,job_id,task_id, QuerySet1[i]['Company_Name'])
            
            
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)