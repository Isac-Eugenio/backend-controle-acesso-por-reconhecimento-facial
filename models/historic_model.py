from ipaddress import IPv4Address
from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, Text
from datetime import date, datetime, time

from models.user_model import PermissionEnum


class HistoricModel(BaseModel):
    nome: str
    alias: str
    id: Optional[str] = None
    email: EmailStr
    matricula: Optional[str] = None
    permission_level: PermissionEnum = PermissionEnum.DISCENTE
    mac: Optional[str] = None
    ip: Optional[IPv4Address] = None
    local: Optional[str] = None
    trust: int = None
    data_acesso: Optional[date] = None
    horario_acesso: Optional[time] = None
    log: Optional[Text] = None

    def set_log(self, log: Text):
        self.log = log

    @model_validator(mode="before")
    def fill_defaults(cls, values):
        if values.get("ip") is None:
            values["ip"] = IPv4Address("0.0.0.1")

        if values.get("data_acesso") is None:
            values["data_acesso"] = date.today()

        if values.get("horario_acesso") is None:
            values["horario_acesso"] = datetime.now().time()

        if values.get("trust") is None:
            values["trust"] = 0

        return values
