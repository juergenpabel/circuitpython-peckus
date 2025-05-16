class AbstractJob:

    def __init__(self, job_class: str, job_name: str, job_scope: str):
        self.job_class = job_class
        self.job_name = job_name
        self.job_scope = job_scope


    def begin(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.start() not implemented")


    def update(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.update() not implemented")


    def finish(self) -> None:
        raise NotImplementedError(f"Job<{self.job_class}>.exit() not implemented")


    def name(self) -> bool:
        return self.job_name


    def scope(self) -> str:
        return self.job_scope


    def concurrency(self) -> bool:
        return True

