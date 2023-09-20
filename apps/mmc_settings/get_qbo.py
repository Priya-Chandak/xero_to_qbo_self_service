# import traceback

# from apps import db
# from apps.home.data_util import add_job_status
# from apps.home.models import Jobs
# from apps.home.models import Tool, ToolSettings


# def get_qbo_settings(job_id):
#     try:
#         keys = (
#             db.session.query(Jobs, ToolSettings.keys, ToolSettings.values)
#                 .join(Tool, Jobs.input_account_id == Tool.id)
#                 .join(ToolSettings, ToolSettings.tool_id == Tool.id)
#                 .filter(Jobs.id == job_id)
#                 .all()
#         )
#         for row in keys:
#             if row[1] == "client_id":
#                 client_id = row[2]
#             if row[1] == "client_secret":
#                 client_secret = row[2]
#             if row[1] == "base_url":
#                 base_url1 = row[2]
#             if row[1] == "company_id":
#                 company_id = row[2]
#             if row[1] == "minor_version":
#                 minorversion = row[2]
#             if row[1] == "user_agent":
#                 UserAgent = row[2]
#             if row[1] == "access_token":
#                 access_token = row[2]
#             if row[1] == "refresh_token":
#                 refresh_token = row[2]

#         base_url = f"{base_url1}/v3/company/{company_id}"
#         headers = {
#             "User-Agent": "QBOV3-OAuth2-Postman-Collection",
#             "Accept": "application/json",
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {access_token}",
#         }

#         get_data_header = {
#             "User-Agent": "QBOV3-OAuth2-Postman-Collection",
#             "Accept": "application/json",
#             "Content-Type": "application/text",
#             "Authorization": f"Bearer {access_token}",
#         }

#         report_headers = {
#             "User-Agent": "QBOV3-OAuth2-Postman-Collection",
#             "Accept": "application/json",
#             "Authorization": f"Bearer {access_token}",
#         }

#         return (
#             base_url,
#             headers,
#             company_id,
#             minorversion,
#             get_data_header,
#             report_headers,
#         )

#     except Exception as ex:
#         traceback.print_exc()
#         


import traceback
import requests

from apps import db
from apps.home.data_util import add_job_status
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings
import base64



def get_qbo_settings(job_id):
    try:
        url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        keys = (
            db.session.query(Jobs, ToolSettings.keys, ToolSettings.values)
                .join(Tool, Jobs.input_account_id == Tool.id)
                .join(ToolSettings, ToolSettings.tool_id == Tool.id)
                .filter(Jobs.id == job_id)
                .all()
        )
        for row in keys:
            if row[1] == "client_id":
                client_id = row[2]
            if row[1] == "client_secret":
                client_secret = row[2]
            if row[1] == "base_url":
                base_url1 = row[2]
            if row[1] == "company_id":
                company_id = row[2]
            if row[1] == "minor_version":
                minorversion = row[2]
            if row[1] == "user_agent":
                UserAgent = row[2]
            if row[1] == "access_token":
                access_token = row[2]
            if row[1] == "refresh_token":
                refresh_token = row[2]

        redirect_uri="https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"

        payload=f'grant_type=refresh_token&refresh_token={refresh_token}&redirect_uri={redirect_uri}'

        CLIENT_ID = f"{client_id}"
        CLIENT_SECRET=f"{client_secret}"
        clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
        encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
        auth_code = "%s" % encoded_u
        # print(auth_code)

        headers = {
            'Authorization': "Basic" "  "+  f'{auth_code}',
            'Content-Type': 'application/x-www-form-urlencoded'
            }

        response = requests.request("POST", url, headers=headers, data=payload)
        re = response.json()
        access_token1 = re["access_token"]
        
        base_url = f"{base_url1}/v3/company/{company_id}"
        headers = {
            "User-Agent": "QBOV3-OAuth2-Postman-Collection",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token1}",
        }

        get_data_header = {
            "User-Agent": "QBOV3-OAuth2-Postman-Collection",
            "Accept": "application/json",
            "Content-Type": "application/text",
            "Authorization": f"Bearer {access_token1}",
        }

        report_headers = {
            "User-Agent": "QBOV3-OAuth2-Postman-Collection",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token1}",
        }

        return (
            base_url,
            headers,
            company_id,
            minorversion,
            get_data_header,
            report_headers,
        )

    except Exception as ex:
        traceback.print_exc()
        
