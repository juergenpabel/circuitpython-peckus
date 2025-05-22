from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, peckus_method: str, peckus_data: str, app_data: dict):
        super().__init__('peckus', peckus_method, app_data)
        self.peckus_data = peckus_data


    def requirements(self) -> bool:
        requirements = self.app_data['session'].get('REQUIREMENTS', {})
        if isinstance(requirements, dict) is False or len(requirements) == 0:
            raise ValueError(f"Condition<peckus>.requirements({self.peckus_data}) did not find any requirements")
        for requirement_key, requirement_value in requirements.items():
            if self.app_data['session'].get(requirement_key) != requirement_value:
                return str(False).upper() == self.peckus_data.upper()
        return str(True).upper() == self.peckus_data.upper()


    def requirement(self) -> bool:
        requirements = self.app_data['session'].get('REQUIREMENTS', {})
        if isinstance(requirements, dict) is False or len(requirements) == 0:
            raise ValueError(f"Condition<peckus>.requirements({self.peckus_data}) did not find any requirements")
        if self.peckus_data.count(':') != 2:
            raise ValueError(f"Condition<peckus>.requirement('{self.peckus_data}'): invalid data (expecting 'NAME:bool(VALUE):int(VALIDITY)')")
        requirement_key, requirement_value, requirement_validity = self.peckus_data.split(':', 2)
        if requirement_key not in requirements:
            raise ValueError(f"Condition<peckus>.requirement({self.peckus_data}): query for requirement '{requirement_key}' yielded no matching requirement")
        try:
            requirement_validity = int(requirement_validity)
        except ValueError as e:
            print(f"Condition<peckus>.requirement({self.peckus_data}) validity delta is not a number ('{requirement_validity}'), using 0 instead")
            requirement_validity = 0
        return str(self.app_data['session'].get(requirement_key, None, requirement_validity) == requirements[requirement_key]).upper() == requirement_value.upper()

