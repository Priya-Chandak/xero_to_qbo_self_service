import base64
import traceback

import requests

from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings, XeroQboTokens
from apps.myconstant import *
from redis import StrictRedis
redis = StrictRedis(host='localhost', port=6379, decode_responses=True)


def post_qbo_settings(job_id):
    try:

        job_id_from_redis = redis.get('my_key')

        url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        data1 = db.session.query(XeroQboTokens).filter(
            XeroQboTokens.job_id == job_id_from_redis).first()

        redirect_uri = QBO_REDIRECT
        base_url1 = QBO_BaseURL
        minorversion = 14
        company_id = data1.qbo_company_id
        payload = f'grant_type=refresh_token&refresh_token={data1.qbo_refresh_token}&redirect_uri={redirect_uri}'
        CLIENT_ID = QBO_CI
        CLIENT_SECRET = QBO_CS
        clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
        encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
        auth_code = "%s" % encoded_u

        headers = {
            'Authorization': "Basic" "  " + f'{auth_code}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        re = response.json()
        access_token1 = re["access_token"]
        refresh_token1 = re["refresh_token"]

        db.session.query(XeroQboTokens).filter_by(job_id=job_id_from_redis).update(
            {"qbo_access_token": access_token1})
        db.session.query(XeroQboTokens).filter_by(job_id=job_id_from_redis).update(
            {"qbo_refresh_token": refresh_token1})
        
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
