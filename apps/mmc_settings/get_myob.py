import traceback
from datetime import datetime

import requests

from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings


def get_myob_settings(job_id):
    try:
        url = "https://secure.myob.com/oauth2/v1/authorize/"
        token_generated_on = datetime.now()
        refresh_token_data_id = None
        access_token_data_id = None
        client_id = None
        client_secret = None
        company_file_uri = None
        company_file_id = None
        refresh_token = None
        access_token = None

        keys = (
            db.session.query(Jobs, ToolSettings.keys, ToolSettings.values, ToolSettings.added_on, ToolSettings.id)
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
                refresh_token_data_id = row[4]
            if row[1] == "access_token":
                access_token = row[2]
                access_token_data_id = row[4]
            if row[1] == "redirect_uri":
                redirect_uri = row[2]
            token_generated_on = row[3]

        difference_of_time = (datetime.now() - token_generated_on).seconds

        if difference_of_time >= 1000:
            payload = f"client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token&refresh_token={refresh_token}"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {access_token} ",
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                re = response.json()
                new_access_token = re.get("access_token")
                new_refresh_token = re.get("refresh_token")
                base_url = f"{company_file_uri}/{company_file_id}"
                payload = {}
                headers = {
                    "x-myobapi-key": "44982e0e-1412-4591-b1ff-c48e06db37db",
                    "x-myobapi-version": "v2",
                    "Accept-Encoding": "gzip,deflate",
                    "Authorization": "Bearer {}".format(new_access_token),
                }

                db.session.query(ToolSettings).filter_by(id=access_token_data_id).update(
                    {"values": new_access_token})
                db.session.query(ToolSettings).filter_by(id=refresh_token_data_id).update(
                    {"values": new_refresh_token})
                db.session.commit()
                return payload, base_url, headers
        else:
            base_url = f"{company_file_uri}/{company_file_id}"
            payload = {}
            headers = {
                "x-myobapi-key": "44982e0e-1412-4591-b1ff-c48e06db37db",
                "x-myobapi-version": "v2",
                "Accept-Encoding": "gzip,deflate",
                "Authorization": f"Bearer {access_token}",
            }
            return payload, base_url, headers
    except Exception as ex:
        traceback.print_exc()
