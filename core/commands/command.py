from abc import ABC
from typing import Callable, Generic, Optional, TypeVar, Union
from core.commands.result import Result, Success, Failure

# Tipos genéricos para sucesso e falha
TSuccess = TypeVar("TSuccess")
TFailure = TypeVar("TFailure")


class Command(ABC, Generic[TSuccess, TFailure]):
    """
    Classe base abstrata para implementar o padrão Command.
    Representa uma operação que pode ser executada, retornando um Result (Success ou Failure).
    """

    def __init__(
        self, function: Optional[Callable[[], Result[TSuccess, TFailure]]] = None
    ):
        """
        Inicializa o Command.
        :param function: função que será executada pelo Command, deve retornar um Result
        """
        self._function: Optional[Callable[[], Result[TSuccess, TFailure]]] = function
        self.result: Optional[Result[TSuccess, TFailure]] = None

    def execute(
        self, function: Optional[Callable[[], Result[TSuccess, TFailure]]] = None
    ) -> Result[TSuccess, TFailure]:
        """
        Executa a função associada ao Command.
        :param function: opcional, permite passar uma nova função no momento da execução
        :return: Result (Success ou Failure)
        """

        # Atualiza a função se fornecida
        if function is not None:
            self._function = function

        # Verifica se existe função para execução
        if self._function is None:
            raise ValueError("Nenhuma função fornecida para execução do Command.")

        try:
            # Executa a função e armazena o resultado
            self.result = self._function()
        except Exception as e:
            # Se ocorrer exceção, retorna Failure com a exceção
            self.result = Failure(e)

        return self.result

    def execute_with_param(
        self,
        param: Union[object],
        function: Optional[Callable[[], Result[TSuccess, TFailure]]] = None,
    ) -> Result[TSuccess, TFailure]:
        """
        Executa a função associada ao Command passando um parâmetro.
        :param param: parâmetro a ser passado para a função
        :param function: opcional, permite atualizar a função no momento da execução
        :return: Result (Success ou Failure)
        """

        # Atualiza a função se fornecida
        if function is not None:
            # Aqui a função é chamada com o param para gerar a função interna (parece que é para currying)
            self._function = function(param)

        # Verifica se existe função para execução
        if self._function is None:
            raise ValueError("Nenhuma função fornecida para execução do Command.")

        try:
            # Executa a função passando o parâmetro
            self.result = self._function(param)
        except Exception as e:
            # Se ocorrer exceção, retorna Failure com a exceção
            self.result = Failure(e)

        return self.result
