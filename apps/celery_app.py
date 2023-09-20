from apps import configure_celery

app = configure_celery()

app.conf.imports += ("apps.tasks.myob_to_qbo_task",)
