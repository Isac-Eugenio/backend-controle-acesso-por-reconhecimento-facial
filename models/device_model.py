from ipaddress import IPv4Address
from typing import Optional
from pydantic import BaseModel


class DeviceModel(BaseModel):
    mac: Optional[str] = None
    local: Optional[str] = None
    ip: Optional[IPv4Address] = None

    # Sobrescrevendo model_dump para retornar apenas mac e local
    def model_dump(self, **kwargs):
        return {"mac": self.mac, "local": self.local}

    # Função separada para retornar todos os campos
    def model_dump_all(self, **kwargs):
        return super().model_dump(**kwargs)
