from ipaddress import IPv4Address
from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, Text
from datetime import date, datetime, time

from models.user_model import PermissionEnum


class HistoricModel(BaseModel):
    """
    Modelo que representa um registro de acesso no histórico do sistema.

    Este modelo é utilizado para armazenar informações de cada acesso realizado
    a um ponto de controle (como um ESP32 conectado ao sistema de portas).

    Campos principais:
        - nome / alias: identificação do usuário que realizou o acesso.
        - id / email / matricula: dados do usuário para referência.
        - permission_level: nível de permissão do usuário (discente, docente, administrador).
        - mac / ip / local: identificação do dispositivo utilizado no acesso.
        - trust: indicador de confiança do registro (0 a 100).
        - data_acesso / horario_acesso: data e hora do acesso.
        - log: informações adicionais sobre o registro (ex: debug ou eventos especiais).

    Funcionalidades:
        - set_log(): permite adicionar ou atualizar o log do registro.
        - fill_defaults(): garante valores padrão para ip, data, hora e trust
          caso não sejam fornecidos na criação do objeto.
        - Campos tipados com validação automática (EmailStr, IPv4Address, enums).
    """

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
        """
        Adiciona ou atualiza o campo log deste registro.
        """
        self.log = log

    @model_validator(mode="before")
    def fill_defaults(cls, values):
        """
        Preenche valores padrão caso campos essenciais não sejam fornecidos:
        - ip: 0.0.0.1
        - data_acesso: data atual
        - horario_acesso: hora atual
        - trust: 0
        """
        if values.get("ip") is None:
            values["ip"] = IPv4Address("0.0.0.1")

        if values.get("data_acesso") is None:
            values["data_acesso"] = date.today()

        if values.get("horario_acesso") is None:
            values["horario_acesso"] = datetime.now().time()

        if values.get("trust") is None:
            values["trust"] = 0

        return values
