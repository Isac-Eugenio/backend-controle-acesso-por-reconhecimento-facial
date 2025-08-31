from ipaddress import IPv4Address
from typing import Optional
from pydantic import BaseModel


class DeviceModel(BaseModel):
    """
    Representa um dispositivo de controle de acesso em um sistema, normalmente
    um ESP32 ou microcontrolador equivalente, instalado no local de acesso. 
    Cada dispositivo possui:

        - MAC: endereço físico único para identificação na rede.
        - Local: descrição ou nome do ponto de acesso (ex.: "Laboratório 1").
        - IP: endereço IPv4 do dispositivo, usado para comunicação de rede.

    Este modelo é utilizado para gerenciar dispositivos no banco de dados e
    integrá-los ao sistema de controle de acesso.
    """

    mac: Optional[str] = None
    local: Optional[str] = None
    ip: Optional[IPv4Address] = None

    # Sobrescrevendo model_dump para retornar apenas mac e local
    def model_dump(self, **kwargs):
        """
        Retorna apenas os campos essenciais para identificação do dispositivo
        no contexto de registro e histórico de acessos.

        Returns:
            dict: {"mac": mac, "local": local}
        """
        return {"mac": self.mac, "local": self.local}

    # Função separada para retornar todos os campos
    def model_dump_all(self, **kwargs):
        """
        Retorna todos os campos do dispositivo, incluindo IP, para uso em
        operações de rede ou relatórios completos.

        Returns:
            dict: todos os campos do DeviceModel
        """
        return super().model_dump(**kwargs)
