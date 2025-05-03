from storage import getmount as storage_getmount

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, filesystem_method: str, filesystem_params: str, app_data: dict):
        super().__init__('filesystem', filesystem_method, app_data)
        self.filesystem_params = filesystem_params


    def exists(self) -> bool:
        result = None
        try:
            result = storage_getmount('/').stat(self.filesystem_params)
        except Exception as e:
            pass
        return result is not None


    def mounted(self) -> bool:
        result = False
        try:
            if storage_getmount('/') is not None:
                result = True
        except Exception as e:
            pass
        return str(result).upper() == self.filesystem_params.upper()

    def readonly(self) -> bool:
        return str(storage_getmount('/').readonly).upper() == self.filesystem_params.upper()

