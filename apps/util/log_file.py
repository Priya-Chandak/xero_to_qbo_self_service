import logging
import os


def log_config(job_id):
    logger = logging.getLogger(job_id)
    logger.setLevel(logging.INFO)

    file_name = f"Xero_To_Qbo_{job_id}.log"
    file_handler = logging.FileHandler(os.path.join('apps', 'static', 'logfile', file_name))
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # logger.addHandler(file_handler)

    return file_handler


