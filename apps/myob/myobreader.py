from apps.home.data_util import add_job_status
from apps.home.models import Task
from apps.mmc_settings.all_settings import *
from apps.myob.xero_to_qbo_task import XeroToQbo


def read_data(job_id):
    print("inside read data2")
    try:
        # tool1 = aliased(Tool)
        # tool2 = aliased(Tool)
        # read_result = db.session.execute(
        #     "select t1.account_type as input ,t2.account_type as output from jobs inner join tool t1 on t1.id=jobs.input_account_id inner join tool t2 on t2.id=jobs.output_account_id where jobs.id=:job_id",
        #     {"job_id": job_id})
        # for row in read_result:
        input_tool = 1
        output_tool = 2
        # Get list of tasks added in the job

        # TODO: Check if input tool is excel
        # If yes push data to mongodb in respective tables with job id and task id and some status flag
        # indicating whether the records is pushed or not

        read_tasks = Task.query.filter(Task.job_id == job_id).filter(Task.read != 1).all()
        

        for task in read_tasks:
            if input_tool == 1 and output_tool == 2:
                XeroToQbo.read_data(job_id, task)

            db.session.close()

        # write_result = db.session.execute(
        #     "select t1.account_type as input ,t2.account_type as output from jobs inner join tool t1 on t1.id=jobs.input_account_id inner join tool t2 on t2.id=jobs.output_account_id where jobs.id=:job_id",
        #     {"job_id": job_id})
        # # Output the query result as JSON
        # for row in write_result:
        input_tool = 1
        output_tool = 2 
        # Get list of tasks added in the job

        write_tasks = Task.query.filter(Task.job_id == job_id).filter(Task.write != 1).all()
        

        for task in write_tasks:
            if input_tool == 1 and output_tool == 2:
                XeroToQbo.write_data(job_id, task)

            db.session.close()
    except Exception as ex:
        print(ex)
