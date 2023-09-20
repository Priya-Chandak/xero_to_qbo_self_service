import traceback

import requests

from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings
# from apps.util.qbo_util import add_job_status


def get_myobledger_settings(job_id):
    try:
        url = "https://secure.myob.com/oauth2/v1/authorize/"
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
            if row[1] == "company_file_uri":
                company_file_uri = row[2]
            if row[1] == "company_file_id":
                company_file_id = row[2]
            if row[1] == "refresh_token":
                refresh_token = row[2]
            if row[1] == "access_token":
                access_token = row[2]
            if row[1] == "redirect_uri":
                redirect_uri = row[2]
        payload = f"client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token&refresh_token={refresh_token}"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {access_token} ",
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        re = response.json()
        access_token1 = re["access_token"]

        base_url = f"{company_file_uri}/{company_file_id}"
        payload = {}

        headers = {
            "x-myobapi-key": "44982e0e-1412-4591-b1ff-c48e06db37db",
            "x-myobapi-version": "v2",
            "Accept-Encoding": "gzip,deflate",
            "Authorization": "Bearer {}".format(access_token1),
        }
        return payload, base_url, headers

    except Exception as ex:
        traceback.print_exc()
        
