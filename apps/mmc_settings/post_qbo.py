# import traceback

# from apps import db
# from apps.home.data_util import add_job_status
# from apps.home.models import Jobs
# from apps.home.models import Tool, ToolSettings


# def post_qbo_settings(job_id):
#     try:
#         keys = (
#             db.session.query(Jobs, ToolSettings.keys, ToolSettings.values)
#                 .join(Tool, Jobs.output_account_id == Tool.id)
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


import base64
import traceback

import requests

from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings,XeroQboTokens


def post_qbo_settings(job_id):
    try:
        url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        data1 = db.session.query(XeroQboTokens).filter(XeroQboTokens.job_id == job_id).first()
       
        # keys = (
        #     db.session.query(Jobs, ToolSettings.keys, ToolSettings.values)
        #     .join(Tool, Jobs.output_account_id == Tool.id)
        #     .join(ToolSettings, ToolSettings.tool_id == Tool.id)
        #     .filter(Jobs.id == job_id)
        #     .all()
        # )
        # for row in keys:
        #     if row[1] == "client_id":
        #         client_id = row[2]
        #     if row[1] == "client_secret":
        #         client_secret = row[2]
        #     if row[1] == "base_url":
        #         base_url1 = row[2]
        #     if row[1] == "company_id":
        #         company_id = row[2]
        #     if row[1] == "minor_version":
        #         minorversion = row[2]
        #     if row[1] == "user_agent":
        #         UserAgent = row[2]
        #     if row[1] == "access_token":
        #         access_token = row[2]
        #     if row[1] == "refresh_token":
        #         refresh_token = row[2]

        redirect_uri = 'http://localhost:5000/data_access'
        base_url1="https://sandbox-quickbooks.api.intuit.com"
        minorversion=14
        company_id=data1.qbo_company_id
        payload = f'grant_type=refresh_token&refresh_token={data1.qbo_refresh_token}&redirect_uri={redirect_uri}'
        CLIENT_ID = 'ABpWOUWtcEG1gCun5dQbQNfc7dvyalw5qVF97AkJQcn5Lh09o6'
        CLIENT_SECRET = 'LepyjXTADW592Dq5RYUP8UbGLcH5xtqDQhrf2xJN'
        clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
        encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
        auth_code = "%s" % encoded_u
        # print(auth_code)
        # headers = {
        #     'Authorization': 'Basic QUJpVUxJQUpBRUxFdVpDMWRuenZUZjBYZEhsSjlWWUJob0swZ3pQYTBoV3RSOWdsZWU6bVZFV0p2UXlLRjF1VmdmUEFMa1JXb05Ybk55OTBnTHEyUXhOcjA4UQ==',
        #     'Content-Type': 'application/x-www-form-urlencoded'
        #     }

        headers = {
            'Authorization': "Basic" "  " + f'{auth_code}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        re = response.json()
        access_token1 = re["access_token"]

        base_url = f"{base_url1}/v3/company/{data1.qbo_company_id}"
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
