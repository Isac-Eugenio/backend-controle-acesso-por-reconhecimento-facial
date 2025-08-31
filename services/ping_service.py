import platform
import subprocess
from typing import Callable

from core.commands.command import Command
from core.commands.result import Result, Success, Failure


class PingService:
    """
    Serviço para verificar a conectividade de rede com um IP específico.
    - Executa ping usando subprocess, adaptando parâmetros para Windows ou Linux.
    - Fornece resultado síncrono como True/False.
    - Armazena último resultado no atributo `ping_result`.
    """

    def __init__(self, ip: str):
        """
        Executa o comando de ping no IP fornecido.
        Retorna:
        - Success se o ping respondeu (código 0)
        - Failure caso contrário ou se houver exceção
        """

        self.ip = ip
        # Inicializa o Command com a função de ping
        self.command = Command(self._ping_command)
        self.ping_result = self.command.execute()

    def _ping_command(self) -> Result[int, int]:
        # Define o parâmetro correto baseado no sistema operacional
        param = "-n" if platform.system().lower() == "windows" else "-c"

        # Monta o comando de ping de forma segura
        command = ["ping", param, "1", self.ip]

        try:
            # Executa o ping
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            if result.returncode == 0:
                return Success(result.returncode)
            else:
                return Failure(result.returncode)

        except Exception as e:
            return Failure(e)

    def ping(self) -> bool:
        """
        Executa o ping usando _ping_command e retorna True se bem-sucedido, False caso contrário.
        """
        result = self.command.execute()
        return result.is_success
