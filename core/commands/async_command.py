from typing import Optional, Callable, Union, Awaitable
from core.commands.command import Command
from core.commands.result import Result, Failure, TSuccess, TFailure


class AsyncCommand(Command[TSuccess, TFailure]):
    """
    Classe que estende Command para suportar execução assíncrona.
    Permite encapsular funções async que retornam Result (Success ou Failure).
    """

    async def execute_async(
        self,
        function: Optional[Callable[[], Awaitable[Result[TSuccess, TFailure]]]] = None,
    ) -> Result[TSuccess, TFailure]:
        """
        Executa a função assíncrona associada ao Command.
        :param function: opcional, permite passar uma nova função assíncrona
        :return: Result (Success ou Failure)
        """

        # Atualiza a função se fornecida
        if function is not None:

            async def wrapper():
                return await function()

            # Salva o wrapper no atributo interno _function
            self._function = wrapper

        # Garante que existe função para execução
        if self._function is None:
            raise ValueError("Nenhuma função fornecida para execução do AsyncCommand.")

        try:
            # Executa a função assíncrona e aguarda o resultado
            self.result = await self._function()
        except Exception as e:
            # Captura exceções e transforma em Failure
            self.result = Failure(
                _value=str(e),
                details=getattr(e, "args", None),
                log="Erro no AsyncCommand",
            )

        return self.result

    async def execute_async_with_param(
        self,
        param: object,
        function: Optional[
            Callable[[object], Awaitable[Result[TSuccess, TFailure]]]
        ] = None,
    ) -> Result[TSuccess, TFailure]:
        """
        Executa a função assíncrona passando um parâmetro.
        :param param: parâmetro a ser passado para a função
        :param function: opcional, permite atualizar a função no momento da execução
        :return: Result (Success ou Failure)
        """

        # Atualiza a função se fornecida, criando um wrapper que passa o parâmetro
        if function is not None:
            async def wrapper():
                return await function(param)

            self._function = wrapper

        # Garante que existe função para execução
        if self._function is None:
            raise ValueError("Nenhuma função fornecida para execução do AsyncCommand.")

        try:
            # Executa a função assíncrona com o parâmetro
            self.result = await self._function()
        except Exception as e:
            # Captura exceções e transforma em Failure
            self.result = Failure(
                _value=str(e),
                details=getattr(e, "args", None),
                log="Erro no AsyncCommand",
            )

        return self.result
