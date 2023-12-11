import base64
import traceback

import requests
from redis import StrictRedis

from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings, XeroQboTokens
from apps.myconstant import *
redis = StrictRedis(host='localhost', port=6379, decode_responses=True)


def get_xero_setting_for_report(job_id):
    try:
        url = "https://identity.xero.com/connect/token?="

        data1 = db.session.query(XeroQboTokens).filter(
            XeroQboTokens.job_id == job_id).first()

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

        db.session.query(XeroQboTokens).filter_by(job_id=job_id).update(
            {"xero_access_token": new_access_token})
        db.session.query(XeroQboTokens).filter_by(job_id=job_id).update(
            {"xero_refresh_token": new_refresh_token})

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

    except Exception as ex:
        traceback.print_exc()
