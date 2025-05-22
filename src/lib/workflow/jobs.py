from re import match as re_match
from gc import collect as gc_collect

from peckus.workflow.job import AbstractJob as Job


class Jobs:

    def __init__(self, jobs: list, app_data: dict):
        self.app_data = app_data
        if 'job_classes' not in self.app_data:
            self.app_data['job_classes'] =  {}
        self.jobs = []
        for job in jobs:
            if isinstance(job, dict) is False:
                raise ValueError(f"Invalid job definitions (must be a dict): {job}")
            if 'job' not in job:
                raise ValueError(f"Missing 'job' item in job}")
            if 'name' not in job:
                raise ValueError(f"Missing 'name' item in job}")
            if 'data' not in job:
                raise ValueError(f"Missing 'data' item in job}")
            job_classname = job['job'].upper()
            job_class = None
            if job_classname in self.app_data['job_classes']:
                job_class = self.app_data['job_classes'][job_classname]
            else:
                exec(f'from peckus.workflow.job.{job_classname.lower()} import Job as {job_classname}')
                self.app_data['job_classes'][job_classname] = eval(job_classname)
            self.add(self.app_data['job_classes'][job_classname](job['name'], job['data'], self.app_data))


    def add(self, job: Job) -> None:
        self.jobs.append(job)


    def begin(self) -> None:
        gc_collect()
        for job in self.jobs:
            try:
                job.begin()
            except Exception as e:
                print(f"Job<{job.job_class}>.begin() raised an exception: {e}")


    def update(self) -> None:
        gc_collect()
        for job in self.jobs:
            try:
                job.update()
            except Exception as e:
                print(f"Job<{job.job_class}>.update() raised an exception: {e}")


    def finish(self) -> None:
        gc_collect()
        for job in self.jobs:
            try:
                job.finish()
            except Exception as e:
                print(f"Job<{job.job_class}>.finish() raised an exception: {e}")

