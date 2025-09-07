from queue import Queue

from .console_run import console_run
from .RunParallel import RunParallel


def collectstatic():
    console_run("python manage.py collectstatic --noinput")


def makemigrations():
    console_run("python manage.py makemigrations")


def migrate():
    console_run("python manage.py migrate")


def runserver():
    console_run("python -Wa manage.py runserver 0.0.0.0:8080")


class RP(RunParallel):
    def static_update(self, result: dict, q: Queue):
        collectstatic()

    def database_update(self, result: dict, q: Queue):
        makemigrations()
        migrate()


def django_runserver():
    try:
        RP().run_multi_threading()
        runserver()
    except KeyboardInterrupt:
        pass
