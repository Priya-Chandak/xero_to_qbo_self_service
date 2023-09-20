import traceback
import base64
import requests
from apps import db
from apps.home.data_util import add_job_status
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings


def get_xero_settings(job_id):
    try:
        url="https://identity.xero.com/connect/token?="
        

        keys = (
            db.session.query(Jobs, ToolSettings.keys, ToolSettings.values,ToolSettings.id)
                .join(Tool, Jobs.input_account_id == Tool.id)
                .join(ToolSettings, ToolSettings.tool_id == Tool.id)
                .filter(Jobs.id == job_id)
                .all()
        )
    

        data1 = (
            db.session.query(ToolSettings.id, Tool.tool_name, Tool.account_type, Tool.id, ToolSettings.keys, ToolSettings.values)
            .join(Tool, ToolSettings.tool_id == Tool.id)
            .filter(Tool.account_type == "Xero")
            .all())

        

        for row in keys:
            if row[1] == "client_id":
                client_id = row[2]
            if row[1] == "client_secret":
                client_secret = row[2]
            if row[1] == "company_file_uri":
                company_file_uri = row[2]
            if row[1] == "xero-tenant-id":
                xero_tenant_id = row[2]
            if row[1] == "refresh_token":
                refresh_token = row[2]
                refresh_token_data_id = row[3]
            if row[1] == "access_token":
                access_token = row[2]
                access_token_data_id =row[3]
            if row[1] == "re_directURI":
                re_directURI = row[2]
            if row[1] == "scopes":
                scopes = row[2]
            if row[1] == "state":
                state = row[2]



        CLIENT_ID = f"{client_id}"
        CLIENT_SECRET=f"{client_secret}"
        clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
        encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
        auth_code = "%s" % encoded_u


        # for row in data1:
        #     if row[4] == "client_id":
        #         client_id ==  row[5]
        #     if row[4] == "client_secret":
        #         client_secret = row[5]
        #     if row[4] == "company_file_uri":
        #         company_file_uri = row[5]
        #     if row[4] == "xero-tenant-id":
        #         xero_tenant_id1 = row[5]
        #     if row[4] == "refresh_token":
        #         refresh_token1 = row[5]
        #         refresh_token_data_id1 = row[2]
        #     if row[4] == "access_token":
        #         access_token1 = row[5]
        #         access_token_data_id1 =row[2]
        #     if row[4] == "re_directURI":
        #         re_directURI = row[5]
        #     if row[4] == "scopes":
        #         scopes = row[5]
        #     if row[4] == "state":
        #         state = row[5]

        payload = {'grant_type': 'refresh_token',
        'refresh_token': f'{refresh_token}',
        'client_id': f'{client_id}',
        }
        headers = {
              'Authorization': "Basic" "  " + f'{auth_code}',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        re=response.json()
        new_access_token=re['access_token']
        new_refresh_token = re['refresh_token']
        db.session.query(ToolSettings).filter_by(id=access_token_data_id).update({"values": new_access_token})
        db.session.query(ToolSettings).filter_by(id=refresh_token_data_id).update({"values": new_refresh_token})

        for row in data1:
            if row[4] == "refresh_token":
                refresh_token_data_id1= row[0]
                db.session.query(ToolSettings).filter_by(id=refresh_token_data_id1).update({"values":new_refresh_token})
                # row[5] = new_refresh_token
            if row[4] == "access_token":
                access_token_data_id1 = row[0]
                db.session.query(ToolSettings).filter_by(id=access_token_data_id1).update({"values": new_access_token})

        db.session.commit()
        base_url = "https://api.xero.com/api.xro/2.0"
        payload = ""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Xero-Tenant-Id": f"{xero_tenant_id}",
            "Authorization": f"Bearer {new_access_token}",
        }

        return payload, base_url, headers

    except Exception as ex:
        traceback.print_exc()
