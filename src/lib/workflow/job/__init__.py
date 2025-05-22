class AbstractJob:

    def __init__(self, job_class: str, job_name: str, app_data: dict):
        self.app_data = app_data
        if job_class not in self.app_data:
            self.app_data[job_class] = {}
        self.job_class = job_class
        self.job_name = job_name
        self.app_data = app_data


    def begin(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.start() not implemented")


    def update(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.update() not implemented")


    def finish(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.exit() not implemented")

