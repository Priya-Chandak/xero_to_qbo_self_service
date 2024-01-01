# import base64
# import traceback

# import requests
# from redis import StrictRedis
# from apps.util.log_file import log_config

# from apps import db
# from apps.home.models import Jobs
# from apps.home.models import Tool, ToolSettings, XeroQboTokens
# from apps.myconstant import *
# import logging
# redis = StrictRedis(host='localhost', port=6379, decode_responses=True)
# import time

# def get_xero_settings(job_id):
#     print("inside get_xero_settings------------------------------")
#     log_config1=log_config(job_id)
    
#     try:
#         url = "https://identity.xero.com/connect/token?="

#         job_id_from_redis = redis.get('my_key')

#         data1 = db.session.query(XeroQboTokens).filter(
#             XeroQboTokens.job_id == job_id_from_redis).first()

#         # keys = (
#         #     db.session.query(Jobs, ToolSettings.keys, ToolSettings.values, ToolSettings.id)
#         #     .join(Tool, Jobs.input_account_id == Tool.id)
#         #     .join(ToolSettings, ToolSettings.tool_id == Tool.id)
#         #     .filter(Jobs.id == job_id)
#         #     .all()
#         # )

#         # data1 = (
#         #     db.session.query(ToolSettings.id, Tool.tool_name, Tool.account_type, Tool.id, ToolSettings.keys,
#         #                      ToolSettings.values)
#         #     .join(Tool, ToolSettings.tool_id == Tool.id)
#         #     .filter(Tool.account_type == "Xero")
#         #     .all())

#         # for row in keys:
#         #     if row[1] == "client_id":
#         #         client_id = row[2]
#         #     if row[1] == "client_secret":
#         #         client_secret = row[2]
#         #     if row[1] == "company_file_uri":
#         #         company_file_uri = row[2]
#         #     if row[1] == "xero-tenant-id":
#         #         xero_tenant_id = row[2]
#         #     if row[1] == "refresh_token":
#         #         refresh_token = row[2]
#         #         refresh_token_data_id = row[3]
#         #     if row[1] == "access_token":
#         #         access_token = row[2]
#         #         access_token_data_id = row[3]
#         #     if row[1] == "re_directURI":
#         #         re_directURI = row[2]
#         #     if row[1] == "scopes":
#         #         scopes = row[2]
#         #     if row[1] == "state":
#         #         state = row[2]

#         client_id = XERO_CI
#         client_secret = XERO_CS

#         CLIENT_ID = f"{client_id}"
#         CLIENT_SECRET = f"{client_secret}"
#         clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
#         encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
#         auth_code = "%s" % encoded_u
#         print(data1.xero_access_token,"data1.xero_access_token-----------------------")
#         payload = ""
#         headers = {
#             "Content-Type": "application/json",
#             "Accept": "application/json",
#             "Xero-Tenant-Id": f"{data1.xero_company_id}",
#             "Authorization": f"Bearer {data1.xero_access_token}",
#         }

#         base_url = "https://api.xero.com/api.xro/2.0"
            
#         main_url = f"{base_url}/Accounts"
#         print(main_url)
#         response1 = requests.request("GET", main_url, headers=headers, data=payload)
#         time.sleep(1)
#         print(response1.status_code,"========================================================")
#         if response1.status_code != 200:
#             print("token expired-------------------", response1.status_code)
#             payload = {'grant_type': 'refresh_token',
#                     'refresh_token': f'{data1.xero_refresh_token}',
#                     'client_id': f'{client_id}',
#                     }
#             headers = {
#                 'Authorization': "Basic" "  " + f'{auth_code}',
#             }

#             response = requests.request("POST", url, headers=headers, data=payload)
#             re = response.json()
#             new_access_token = re['access_token']
#             new_refresh_token = re['refresh_token']

#             print(new_access_token,"new_access_token--------------------------------------")

#             db.session.query(XeroQboTokens).filter_by(job_id=job_id_from_redis).update(
#                 {"xero_access_token": new_access_token})
#             db.session.query(XeroQboTokens).filter_by(job_id=job_id_from_redis).update(
#                 {"xero_refresh_token": new_refresh_token})
            
#             print("new token updated")
#             # db.session.query(XeroQboTokens).filter_by(XeroQboTokens.job_id==job_id_from_redis).update(
#             #     {"xero_access_token": new_access_token})
#             # db.session.query(XeroQboTokens).filter_by(XeroQboTokens.job_id==job_id_from_redis).update(
#             #     {"xero_refresh_token": new_refresh_token})

#             db.session.commit()

#             payload = ""
#             headers = {
#                 "Content-Type": "application/json",
#                 "Accept": "application/json",
#                 "Xero-Tenant-Id": f"{data1.xero_company_id}",
#                 "Authorization": f"Bearer {new_access_token}",
#             }
#         else:
#             print("token not expired -----------------------------------")
#             payload = ""
#             headers = {
#                 "Content-Type": "application/json",
#                 "Accept": "application/json",
#                 "Xero-Tenant-Id": f"{data1.xero_company_id}",
#                 "Authorization": f"Bearer {data1.xero_access_token}",
#             }

#         return payload, base_url, headers

#     except Exception as ex:
#         logging.error(ex, exc_info=True)
#         traceback.print_exc()


import base64
import traceback
from datetime import datetime

import requests
from redis import StrictRedis

from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings, XeroQboTokens
from apps.myconstant import *
redis = StrictRedis(host='localhost', port=6379, decode_responses=True)


def get_xero_settings(job_id):
    try:
        url = "https://identity.xero.com/connect/token?="

        job_id_from_redis = redis.get('my_key')

        data1 = db.session.query(XeroQboTokens).filter(
            XeroQboTokens.job_id == job_id_from_redis).first()

        difference_of_time = (datetime.now() - data1.created_at).seconds
        if difference_of_time >= 1200:

            client_id = XERO_CI
            client_secret = XERO_CS

            CLIENT_ID = f"{client_id}"
            CLIENT_SECRET = f"{client_secret}"
            clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
            encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
            auth_code = "%s" % encoded_u
            payload = {'grant_type': 'refresh_token',
                    'refresh_token': f'{data1.xero_refresh_token}',
                    'client_id': f'{client_id}',
                    }
            headers = {
                'Authorization': "Basic" "  " + f'{auth_code}',
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            re = response.json()
            new_access_token = re['access_token']
            new_refresh_token = re['refresh_token']

            db.session.query(XeroQboTokens).filter_by(job_id=job_id_from_redis).update(
                {"xero_access_token": new_access_token})
            db.session.query(XeroQboTokens).filter_by(job_id=job_id_from_redis).update(
                {"xero_refresh_token": new_refresh_token})
            
            db.session.query(XeroQboTokens).filter_by(job_id=job_id_from_redis).update(
                {"created_at": datetime.now()})
            
            db.session.commit()

            base_url = "https://api.xero.com/api.xro/2.0"
            payload = ""
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Xero-Tenant-Id": f"{data1.xero_company_id}",
                "Authorization": f"Bearer {new_access_token}",
            }

            return payload, base_url, headers
        
        else:
            base_url = "https://api.xero.com/api.xro/2.0"
            payload = ""
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Xero-Tenant-Id": f"{data1.xero_company_id}",
                "Authorization": f"Bearer {data1.xero_access_token}",
            }

            return payload, base_url, headers


    except Exception as ex:
        traceback.print_exc()
