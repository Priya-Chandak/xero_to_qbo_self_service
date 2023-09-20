import traceback

from apps import db
from apps.home.models import Jobs, JobExecutionStatus, Task, TaskExecutionStatus, TaskExecutionStep

traceback.print_exc()


def add_job_status(job_id, status):
    session = None
    try:
        job_execution_status = JobExecutionStatus()
        job_execution_status.job_id = job_id
        job_execution_status.status = status
        db.session.add(job_execution_status)
        db.session.commit()
    except Exception as e:
        pass
    finally:
        if session is not None:
            session.close()


def add_task_status(job_id, table_name, operation="read", started_or_complete="started"):
    session = None
    try:
        task_execution_status = TaskExecutionStatus()
        task_execution_status.job_id = job_id
        # task_execution_status.task_id =Task.id
        # task_started_or_complete = "started......."

        if started_or_complete == "complete reading":

            task_execution_status.read_successful = 1
            # task_execution_status=task_started_or_complete
        else:
            task_execution_status.read_successful = 0

        if started_or_complete == "complete writing":
            task_execution_status.write_successful = 1
            # task_execution_status=task_started_or_complete
        else:
            task_execution_status.write_successful = 0

        # jb=JobExecutionStatus(job_id,status,start_time=time.strftime('%Y-%m-%d %H:%M:%S'),end_time=time.strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(task_execution_status)
        db.session.commit()
    except Exception as e:
        import traceback

        traceback.print_exc()
    finally:
        if session is not None:
            session.close()


# def add_task_status(job_id, table_name, operation="read", started_or_complete="started"):
#     session = None
#     try:
#         task_execution_status = TaskExecutionStatus()
#         task_execution_status.job_id = job_id
#         task_execution_status.task_id = Task.id
#         task_execution_status = "started......."
#         if started_or_complete == "complete":
#             job_started_or_complete = "completed"

#         if started_or_complete == "reading completed":
#             task_execution_status.read_successful = True
#             task_execution_status="reading completed......."
#         else:
#             task_execution_status.read_successful = False

#         if started_or_complete == "writing completed":
#             task_execution_status.write_successful = True
#             task_execution_status ="writing completed......."
#         else:
#             task_execution_status.write_successful = False

#         db.session.add(task_execution_status)
#         db.session.commit()
#     except Exception as e:
#         import traceback

#         traceback.print_exc()
#     finally:
#         if session is not None:
#             session.close()


def get_job_details(job_id):
    job_details = db.session.query(Jobs).get(job_id)
    start_date = job_details.start_date
    end_date = job_details.end_date
    return start_date, end_date

# job_id
def update_task_execution_status(task_id, status, task_type):
    task = Task.query.filter(
        # Task.job_id == job_id,
        Task.id == task_id
    ).first()
    if task_type == "read":
        task.read = status
    else:
        task.write = status
    db.session.add(task)
    db.session.commit()

# job_id
def write_task_execution_step(task_id, status, step, error=None):
    task_execution_step = TaskExecutionStep()
    task_execution_step.task_id = task_id
    # task_execution_step.job_id = job_id
    task_execution_step.step = step
    task_execution_step.status = status
    task_execution_step.error = error
    db.session.add(task_execution_step)
    db.session.commit()
