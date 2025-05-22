import builtins


class Print(object):

    def __init__(self, enabled: bool=True):
        super().__init__()
        self.enabled = enabled
        self.builtins_print = builtins.print
        builtins.print = self.print


    def enable(self) -> None:
        self.enabled = True


    def disable(self) -> None:
        self.enabled = False


    def print(self, *args) -> None:
        if self.enabled is True:
            self.builtins_print(*args)

