from apps.util.log_file import log_config
import logging
import os


def log_config(job_id):
    print(job_id,"log_config-------------------")
    file_name = f"apps/static/logfile/Xero_To_Qbo_{job_id}.log"

    logging.basicConfig(filename=file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    return "Logs Created"

