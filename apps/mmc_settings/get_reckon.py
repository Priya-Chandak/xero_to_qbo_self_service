import traceback

import requests

from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings
# from apps.util.qbo_util import add_job_status


def get_reckon_settings(job_id):
    try:
        url = "https://identity.reckon.com/connect/token"
        keys = (
            db.session.query(Jobs, ToolSettings.keys, ToolSettings.values)
                .join(Tool, Jobs.input_account_id == Tool.id)
                .join(ToolSettings, ToolSettings.tool_id == Tool.id)
                .filter(Jobs.id == job_id)
                .all()
        )

        data1 = (
            db.session.query(ToolSettings.id, Tool.tool_name, Tool.account_type, Tool.id, ToolSettings.keys, ToolSettings.values)
            .join(Tool, ToolSettings.tool_id == Tool.id)
            .filter(Tool.account_type == "Reckon")
            .all())
        
        for row in keys:
            if row[1] == "client_id":
                client_id = row[2]
            if row[1] == "client_secret":
                client_secret = row[2]
            if row[1] == "id_secret_encoded":
                id_secret_encoded = row[2]
            if row[1] == "redirect_url":
                redirect_url = row[2]
            if row[1] == "username":
                username = row[2]
            if row[1] == "password":
                password = row[2]
            if row[1] == "token":
                token = row[2]
            if row[1] == "refresh_token":
                refresh_token = row[2]
            if row[1] == "url":
                url = row[2]
            if row[1] == "book":
                book = row[2]
            

        payload = f"grant_type=refresh_token&refresh_token={refresh_token}&redirect_uri={redirect_url}"  

        headers = {
                'Authorization': f"Basic {id_secret_encoded}",
                'Content-Type': 'application/x-www-form-urlencoded',
               
            }
        response = requests.request("POST", url, headers=headers, data=payload)

        re = response.json()
        new_access_token = re["access_token"]
        new_refresh_token = re["refresh_token"]


        for row in data1:
            if row[4] == "refresh_token":
                refresh_token_data_id1 = row[0]
                db.session.query(ToolSettings).filter_by(id=refresh_token_data_id1).update(
                    {"values": new_refresh_token})
            if row[4] == "token":
                access_token_data_id1 = row[0]
                db.session.query(ToolSettings).filter_by(id=access_token_data_id1).update({"values": new_access_token})


        db.session.commit()
        base_url = f"{url}/{book}"
        payload = {}

        headers = {
            "x-myobapi-key": "44982e0e-1412-4591-b1ff-c48e06db37db",
            "x-myobapi-version": "v2",
            "Accept-Encoding": "gzip,deflate",
            "Authorization": "Bearer {}".format(new_access_token),
        }
        post_headers = {
            'Authorization': f'Bearer {new_access_token}',
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': 'bdddd3c7a4034e538e2fea7f61e92aa5' 
            }
        
        get_headers = {
            'Authorization': f'Bearer {new_access_token}',
            'Ocp-Apim-Subscription-Key': 'bdddd3c7a4034e538e2fea7f61e92aa5' 
            }
        
        return payload, base_url, headers,book,post_headers,get_headers

    except Exception as ex:
        traceback.print_exc()
        
