class AbstractJob:

    def __init__(self, job_class: str, job_name: str):
        self.job_class = job_class
        self.job_name = job_name


    def begin(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.start() not implemented")


    def update(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.update() not implemented")


    def finish(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.exit() not implemented")

