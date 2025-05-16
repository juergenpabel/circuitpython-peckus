from re import match as re_match
from gc import collect as gc_collect

from peckus.workflow.job import AbstractJob as Job

class JobScope:
    WORKFLOW = 'workflow'
    STATE    = 'state'


class Jobs:

    def __init__(self, jobs: list, app_data: dict):
        self.app_data = app_data
        if 'job_classes' not in self.app_data:
            self.app_data['job_classes'] =  {}
        if 'jobs_instances' not in self.app_data:
            self.app_data['job_instances'] =  {'peckus.workflow.job.action': []}
        self.jobs = []
        for job in jobs:
            if isinstance(job, dict) is False:
                raise ValueError(f"Invalid job definitions (must be a dict): {job}")
            if 'scope' not in job:
                job['scope'] = JobScope.STATE
            if 'job' not in job:
                raise ValueError(f"Missing 'job' item in job}")
            if job['scope'] not in [JobScope.WORKFLOW, JobScope.STATE]:
                raise ValueError(f"Invalid 'scope' item in job}")
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
            self.add(self.app_data['job_classes'][job_classname](job['name'], job['data'], job['scope']), job_classname)


    def add(self, job: Job, job_classname: str) -> None:
        job_classname = job_classname.upper()
        if job_classname not in self.app_data['job_instances']:
            self.app_data['job_instances'][job_classname] = []
        if job.concurrency() is False:
            for concurrent_job in self.app_data['job_instances'][job_classname].copy():
                if concurrent_job.scope() != JobScope.WORKFLOW or job.scope() != JobScope.WORKFLOW:
                    raise ValueError(f"Concurrent instances of non-concurrent job class 'peckus.workflow.job.{job['job'].lower()}' running in workflows: " \
                                      "'{job.name()}', '{concurrent_job.name()}'")
                concurrent_job.finish() # TODO: concurrent jobs in different workflows
                self.app_data['job_instances'][job_classname].remove(concurrent_job)
        self.jobs.append(job)
        self.app_data['job_instances'][job_classname].append(job)


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
            if job.scope() == JobScope.STATE:
                try:
                    job.finish()
                except Exception as e:
                    print(f"Job<{job.job_class}>.finish() raised an exception: {e}")
                for job_classname, job_instances in self.app_data['job_instances'].items():
                    if job in job_instances:
                        job_instances.remove(job)

