from apps.home.data_util import add_job_status
from apps.home.models import Task
from apps.mmc_settings.all_settings import *
from apps.myob.delete_to_qbo import DeleteToQbo
from apps.myob.xero_to_qbo_task import XeroToQbo


def read_data(job_id):
    try:
        tool1 = aliased(Tool)
        tool2 = aliased(Tool)
        read_result = db.session.execute(
            "select t1.account_type as input ,t2.account_type as output from jobs inner join tool t1 on t1.id=jobs.input_account_id inner join tool t2 on t2.id=jobs.output_account_id where jobs.id=:job_id",
            {"job_id": job_id})
        for row in read_result:
            input_tool = row[0]
            output_tool = row[1]
        # Get list of tasks added in the job

        # TODO: Check if input tool is excel
        # If yes push data to mongodb in respective tables with job id and task id and some status flag
        # indicating whether the records is pushed or not

        read_tasks = Task.query.filter(Task.job_id == job_id).filter(Task.read != 1).all()
        add_job_status(job_id, status=2)

        for task in read_tasks:
            if input_tool == DELETE and output_tool == MYOB:
                DeleteToMyob.read_data(job_id, task)

            if input_tool == DELETE and output_tool == QBO:
                DeleteToQbo.read_data(job_id, task)

            if input_tool == XERO and output_tool == QBO:
                XeroToQbo.read_data(job_id, task)

            db.session.close()

        write_result = db.session.execute(
            "select t1.account_type as input ,t2.account_type as output from jobs inner join tool t1 on t1.id=jobs.input_account_id inner join tool t2 on t2.id=jobs.output_account_id where jobs.id=:job_id",
            {"job_id": job_id})
        # Output the query result as JSON
        for row in write_result:
            input_tool = row[0]
            output_tool = row[1]
        # Get list of tasks added in the job

        write_tasks = Task.query.filter(Task.job_id == job_id).filter(Task.write != 1).all()
        add_job_status(job_id, status=2)

        for task in write_tasks:
            if input_tool == DELETE and output_tool == MYOB:
                DeleteToMyob.write_data(job_id, task)

            if input_tool == DELETE and output_tool == QBO:
                DeleteToQbo.write_data(job_id, task)

            if input_tool == XERO and output_tool == QBO:
                XeroToQbo.write_data(job_id, task)

            db.session.close()

        # delete_result = db.session.execute("select t1.account_type as input ,t2.account_type as output from jobs inner join tool t1 on t1.id=jobs.input_account_id inner join tool t2 on t2.id=jobs.output_account_id where jobs.id=:job_id", {"job_id":job_id})
        # # Output the query result as JSON
        # for row in delete_result:
        #     input_tool=row[0]
        #     output_tool=row[1]
        # # Get list of tasks added in the job

        # delete_tasks = Task.query.filter(Task.job_id == job_id).filter(Task.delete != 1).all()

        # for task in delete_tasks:
        #     print("hasiixiax")
        #     if input_tool == DELETE and output_tool == MYOB:
        #         DeleteToMyob.delete_data(job_id, task)

        #     db.session.close()



    except Exception as ex:
        print(ex)
