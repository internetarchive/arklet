import subprocess


def main():
    cmd = ["python", "manage.py", "runserver", "0.0.0.0:8000"]
    subprocess.run(cmd)


def migrate():
    cmd = ["python", "manage.py", "migrate"]
    subprocess.run(cmd)


def createsuperuser():
    cmd = ["python", "manage.py", "createsuperuser"]
    subprocess.run(cmd)
