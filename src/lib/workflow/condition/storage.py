from storage import getmount as storage_getmount

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, storage_method: str, storage_criteria: str, app_data: dict):
        super().__init__("storage", storage_method, app_data)
        self.storage_criteria = storage_criteria

    def exists(self) -> bool:
        result = None
        try:
            result = storage_getmount('/').stat(self.storage_criteria)
        except Exception as e:
            return False
        return result is not None

    def mounted(self) -> bool:
        result = False
        try:
            if storage_getmount('/') is not None:
                result = True
        except Exception as e:
            pass
        return str(result).upper() == self.storage_criteria.upper()

    def readonly(self) -> bool:
        return str(storage_getmount('/').readonly).upper() == self.storage_criteria.upper()

