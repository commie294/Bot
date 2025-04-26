from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class VolunteerData:
    name: Optional[str] = None
    region: Optional[str] = None
    help_type: Optional[str] = None
    contact: Optional[str] = None
    contact_other: Optional[str] = None

class UserDataManager:
    def __init__(self, context):
        self._data = context.user_data
    
    @property
    def request_type(self) -> Optional[str]:
        return self._data.get("request_type")
    
    @request_type.setter
    def request_type(self, value: str) -> None:
        self._data["request_type"] = value
    
    @property
    def volunteer_data(self) -> VolunteerData:
        if "volunteer_data" not in self._data:
            self._data["volunteer_data"] = VolunteerData()
        return self._data["volunteer_data"]
    
    def clear(self) -> None:
        self._data.clear()
