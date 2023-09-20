import traceback

from apps import db
from apps.home.data_util import add_job_status
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings


def post_xero_settings(job_id):
    try:
        base_url = "https://api.xero.com/api.xro/2.0"
        keys = (
            db.session.query(Jobs, ToolSettings.keys, ToolSettings.values)
                .join(Tool, Jobs.output_account_id == Tool.id)
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
            if row[1] == "xero-tenant-id":
                xero_tenant_id = row[2]
            if row[1] == "refresh_token":
                refresh_token = row[2]
            if row[1] == "access_token":
                access_token = row[2]
            if row[1] == "re_directURI":
                re_directURI = row[2]
            if row[1] == "scopes":
                scopes = row[2]
            if row[1] == "state":
                state = row[2]

        payload = ""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Xero-Tenant-Id": f"{xero_tenant_id}",
            "Authorization": f"Bearer {access_token}",
            "Cookie": "_abck=CD64D04FFD3FB86E4AB989047BEDF3EE~-1~YAAQlPTfFx5IFfSCAQAAEj+YEgjvqcsS/4lnHxJrLLVp+SwiZxUwXcp8qhdsH4O49QbicBJ8LX5jlCWpwdlhTiOnjslHVoRr+T//SFbtVN/6ssP/wSp4UwEWoNYV8Q2jXfy1wx0aHjP21EoZjycTf3JOkhVJl0rygA6KjZkLqxTEdfyap9KshgeAF+WLk0qUwvimw0wQOWxSbU+pRWp2PFoaUhJvfaIkYSlBr4MIIIXLGd18FBzShcNiS1a2whrx6PI6Fp/4MW2IVVjs/I+UE+whGXypEaa8yNqOn2xpBNSp3b4DFWN808iP+OIWmof/kn2B+sxhGuyVyPA9hH6gGDinGH5pMdU40RS9SIBVZ10gMFM2XL2e+jZp5yDw3yopbWWSmN4=~-1~-1~-1",
        }

        return payload, base_url, headers

    except Exception as ex:
        traceback.print_exc()
        
