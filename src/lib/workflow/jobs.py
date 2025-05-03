from re import match as re_match


class Jobs:

    def __init__(self, jobs: list, appdata: dict):
        if 'job_classes' not in appdata:
            appdata['job_classes'] =  {}
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
            job_class = f'Job_{job['job'].upper()}'
            exec(f'from peckus.workflow.job.{job['job']} import Job as {job_class}')
            appdata['job_classes'][job_class] = eval(job_class)
            self.jobs.append(appdata['job_classes'][job_class](job['name'], job['data']))


    def add(self, job) -> None:
        self.jobs.append(job)


    def begin(self) -> None:
        for job in self.jobs:
            try:
                job.begin()
            except Exception as e:
                print(f"Job<{job.job_class}>.begin() raised an exception: {e}")


    def update(self) -> None:
        for job in self.jobs:
            try:
                job.update()
            except Exception as e:
                print(f"Job<{job.job_class}>.update() raised an exception: {e}")


    def finish(self) -> None:
        for job in self.jobs:
            try:
                job.finish()
            except Exception as e:
                print(f"Job<{job.job_class}>.finish() raised an exception: {e}")

