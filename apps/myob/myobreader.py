from apps.home.data_util import add_job_status
from apps.home.models import Task
from apps.mmc_settings.all_settings import *
from apps.myob.xero_to_qbo_task import XeroToQbo
from apps.myob.report_generation_task import XeroToQboReports


def read_data(job_id):
    print("inside read data2")
    try:
        input_tool = 1
        output_tool = 2
        read_tasks = Task.query.filter(
            Task.job_id == job_id).filter(Task.read != 1).all()
        for task in read_tasks:
            print("read task---------------------------------", task)

            if input_tool == 1 and output_tool == 2:
                XeroToQbo.read_data(job_id, task)
            db.session.close()

        input_tool = 1
        output_tool = 2

        write_tasks = Task.query.filter(
            Task.job_id == job_id).filter(Task.write != 1).all()
        for task in write_tasks:
            print("write task---------------------------------", task)
            if input_tool == 1 and output_tool == 2:
                XeroToQbo.write_data(job_id, task)

            db.session.close()
    except Exception as ex:
        print(ex)


def read_reports(job_id):
    try:
        input_tool = 1
        output_tool = 2

        if input_tool == 1 and output_tool == 2:
            XeroToQboReports.read_data(job_id)
        db.session.close()

    except Exception as ex:
        print(ex)
