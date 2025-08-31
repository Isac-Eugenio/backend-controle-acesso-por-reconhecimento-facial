from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class Response:
    """
    Estrutura de resposta para APIs FastAPI.
    - Contém código HTTP, log, possível erro, detalhes e dados da resposta.
    """

    def __init__(
        self,
        code: int,
        log: str,
        error: Optional[str] = None,
        details: Optional[str] = None,
        data: Optional[Any] = None,
    ):
        self.code = code  # Código HTTP da resposta
        self.log = log  # Mensagem de log ou status
        self.error = error  # Mensagem de erro opcional
        self.details = details  # Informações adicionais sobre erro ou operação
        self.data = data  # Dados de retorno opcionais

    def json(self) -> JSONResponse:
        """
        Retorna a resposta como JSONResponse do FastAPI.
        - Serializa o objeto para JSON.
        - Define Content-Type como application/json.
        - Usa o código HTTP definido em `self.code`.
        """
        return JSONResponse(
            content=jsonable_encoder(self.__dict__),
            status_code=self.code,
            headers={"Content-Type": "application/json"},
        )
