from typing import AsyncGenerator, Callable, Optional
from core.commands.async_command import AsyncCommand
from core.commands.result import *

class StreamCommand(AsyncCommand[TSuccess, TFailure]):
    """
    Extensão do AsyncCommand que permite lidar com streams assíncronas de resultados.
    Ideal para cenários onde múltiplos resultados são produzidos sequencialmente (como processos contínuos ou long-running tasks).
    """

    async def execute_stream(
        self,
        stream: Optional[Callable[[], AsyncGenerator[Result[TSuccess, TFailure], None]]] = None,
    ) -> AsyncGenerator[Result[TSuccess, TFailure], None]:
        """
        Executa uma função assíncrona que retorna um AsyncGenerator de Result.
        - stream: função que retorna AsyncGenerator[Result, None]
        Retorna um generator assíncrono que vai yielding cada Result produzido pela stream.
        """

        if stream is not None:
            # Se a função for fornecida, define como função a ser executada
            self._function = stream

        if self._function is None:
            # Nenhuma função foi fornecida
            raise ValueError("Nenhuma função fornecida para execução do AsyncCommand.")

        try:
            # Itera sobre os resultados da stream de forma assíncrona
            async for task in self._function():
                yield task  # Yield de cada Result produzido

        except Exception as e:
            # Se ocorrer erro, encapsula em Failure e yield
            self.result = Failure(e)
            yield self.result
