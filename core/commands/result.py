from __future__ import annotations
from abc import ABC
from dataclasses import asdict, dataclass, is_dataclass
from typing import Generic, TypeVar, Callable, Union

# Tipos genéricos para sucesso e falha
TSuccess = TypeVar("TSuccess")
TFailure = TypeVar("TFailure")
TNew = TypeVar("TNew")


class Result(ABC, Generic[TSuccess, TFailure]):
    """
    Classe base abstrata para representar o resultado de uma operação.
    Pode estar em três estados:
    - Success: operação bem-sucedida
    - Failure: operação falhou
    - Running: operação em andamento (processo assíncrono)
    """

    @property
    def value(self) -> Union[TSuccess, TFailure, None]:
        """
        Retorna o valor associado ao estado, independente de ser Success, Failure ou Running.
        """
        if isinstance(self, Success):
            return self._value
        elif isinstance(self, Failure):
            return self._value
        elif isinstance(self, Running):
            return self._value
        return None

    @property
    def typeValue(self) -> Result:
        """
        Retorna a própria instância. Útil para encadeamento ou inspeção de tipo.
        """
        return self

    @property
    def is_success(self) -> bool:
        """Retorna True se o resultado for Success."""
        return isinstance(self, Success)

    @property
    def is_failure(self) -> bool:
        """Retorna True se o resultado for Failure."""
        return isinstance(self, Failure)

    @property
    def is_running(self) -> bool:
        """Retorna True se o resultado for Running."""
        return isinstance(self, Running)

    @property
    def success_or_none(self) -> TSuccess | None:
        """Retorna o valor se for Success, caso contrário None."""
        return self._value if isinstance(self, Success) else None

    @property
    def failure_or_none(self) -> TFailure | None:
        """Retorna o valor se for Failure, caso contrário None."""
        return self._value if isinstance(self, Failure) else None

    @property
    def running_or_none(self) -> TSuccess | None:
        """Retorna o valor se for Running, caso contrário None."""
        return self._value if isinstance(self, Running) else None

    def fold(
        self,
        on_success: Callable[[TSuccess], TNew],
        on_failure: Callable[[TFailure], TNew],
        on_running: Callable[[TSuccess], TNew] | None = None,
    ) -> TNew:
        """
        Permite tratar cada estado de maneira funcional.
        Recebe três funções: on_success, on_failure e opcional on_running.
        Retorna o valor retornado pela função correspondente ao estado atual.
        """
        if isinstance(self, Success) and on_running is None:
            return on_success(self._value)
        elif isinstance(self, Running) and on_running is not None:
            return on_running(self._value)
        elif isinstance(self, Failure):
            return on_failure(self._value)
        else:
            raise ValueError("Unhandled state in fold")

    def map(self, func: Callable[[TSuccess], TNew]) -> Result[TNew, TFailure]:
        """
        Aplica uma função ao valor se for Success ou Running.
        Mantém o estado Failure intacto.
        """
        if isinstance(self, Success):
            return Success(func(self._value))
        elif isinstance(self, Running):
            return Running(func(self._value))
        else:  # Failure
            return Failure(self._value)

    def map_failure(self, func: Callable[[TFailure], TNew]) -> Result[TSuccess, TNew]:
        """
        Aplica uma função ao valor se for Failure.
        Mantém Success ou Running intactos.
        """
        if isinstance(self, Failure):
            return Failure(func(self._value))
        elif isinstance(self, Running):
            return Running(self._value)
        else:  # Success
            return Success(self._value)

    def __repr__(self) -> str:
        """Representação em string para debugging."""
        if isinstance(self, Success):
            return f"Success({self._value})"
        elif isinstance(self, Failure):
            return f"Failure({self._value})"
        elif isinstance(self, Running):
            return f"Running({self._value})"
        return "UnknownResult()"

    def to_map(self) -> dict:
        """
        Converte o objeto em dicionário.
        Se for dataclass, usa asdict. Caso contrário, retorna {'_value': valor}.
        """
        if is_dataclass(self):
            return asdict(self)
        return {"_value": getattr(self, "_value", None)}


# Classes concretas para os três estados possíveis
@dataclass(frozen=True)
class Success(Result[TSuccess, TFailure]):
    """Representa uma operação bem-sucedida."""
    _value: TSuccess
    details: str = None
    log: str = None


@dataclass(frozen=True)
class Failure(Result[TSuccess, TFailure]):
    """Representa uma operação que falhou."""
    _value: TFailure
    details: str = None
    log: str = None
    error: bool = False  # flag opcional para indicar erro crítico

@dataclass(frozen=True)
class Running(Result[TSuccess, TFailure]):
    """Representa uma operação em andamento."""
    _value: TSuccess
