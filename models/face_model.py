from typing import Any, List, Tuple, Union, Optional
import cv2
import numpy as np
from pydantic import BaseModel, field_validator, ConfigDict
from core.commands.result import Result, Success, Failure


class FaceModel(BaseModel):
    """
    Modelo que representa uma face detectada e seu encoding para reconhecimento facial.

    Estrutura típica:
        - encodings: vetor de 128 floats representando a face. Pode ser fornecido
          como lista, numpy.ndarray ou string serializada.
        - location: tupla (top, right, bottom, left) indicando a posição da face
          no frame da imagem.
        - frame: frame original da imagem onde a face foi detectada (cv2.Mat ou np.ndarray).

    Funcionalidades:
        - Validação automática de encodings e localização.
        - Conversão entre string e array para armazenamento/serialização.
        - Serialização do modelo para dict, opcionalmente convertendo encodings
          para string.
        - Resultados padronizados usando Success / Failure para tratamento de erros.
    """

    encodings: Union[List[float]] = []
    location: Tuple[int, int, int, int] = ()
    frame: cv2.Mat | np.ndarray[Any, np.dtype[np.integer[Any] | np.floating[Any]]] = (
        None
    )

    # Configuração Pydantic para permitir tipos arbitrários (como np.ndarray)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # -----------------
    # VALIDADORES
    # -----------------

    @field_validator("encodings", mode="before")
    @classmethod
    def validate_encoding(cls, v) -> Union[List[float], np.ndarray]:
        """
        Valida que o encoding fornecido é válido:
        - Deve ter tamanho mínimo de 128.
        - Pode ser string, lista ou np.ndarray.
        Retorna np.ndarray se válido.
        """
        res = cls._validate_encoding(v)
        if res.is_failure:
            raise ValueError(res.details or "Encoding inválido")
        return res.value

    @field_validator("location")
    @classmethod
    def validate_location(cls, v) -> Tuple[int, int, int, int]:
        """
        Valida a localização da face.
        Deve ser uma tupla com exatamente 4 valores.
        """
        if not v or len(v) != 4:
            raise ValueError("Location vazio ou inválido")
        return tuple(v)

    # ------------------------
    # HELPERS DE ENCODING
    # ------------------------

    @staticmethod
    def _validate_encoding(
        encoding: Union[str, List[float], np.ndarray],
    ) -> Result[Union[List[float], np.ndarray], str]:
        """
        Converte e valida o encoding:
        - Se string → converte para np.ndarray.
        - Se lista ou np.ndarray → verifica tamanho mínimo de 128.
        Retorna Success ou Failure.
        """
        try:
            if isinstance(encoding, str):
                arr = np.array(
                    [float(x.strip()) for x in encoding.split(",") if x.strip()]
                )
                if arr.size < 128:
                    return Failure(
                        "Encoding incompleto", details=f"Tamanho recebido: {arr.size}"
                    )
                return Success(
                    arr,
                    log="Encoding convertido de string",
                    details=f"Tamanho: {arr.size}",
                )

            if isinstance(encoding, (list, np.ndarray)):
                length = len(encoding)
                if length < 128:
                    return Failure(
                        "Encoding incompleto", details=f"Tamanho recebido: {length}"
                    )
                return Success(
                    np.array(encoding),
                    log="Encoding válido",
                    details=f"Tamanho: {length}",
                )

            return Failure(
                "Tipo inválido para encoding", details=f"Tipo: {type(encoding)}"
            )

        except Exception as e:
            return Failure("Erro ao validar encoding", details=str(e))

    @staticmethod
    def _encoding_string(encoding: Union[List[float], np.ndarray]) -> Result[str, str]:
        """
        Converte um encoding para string serializada.
        """
        try:
            val_res = FaceModel._validate_encoding(encoding)
            if val_res.is_failure:
                return val_res
            arr = np.array(val_res.value)
            s = ",".join(str(float(x)) for x in arr)
            return Success(
                s, log="Encoding convertido para string", details=f"Tamanho: {arr.size}"
            )
        except Exception as e:
            return Failure("Erro ao converter encoding para string", details=str(e))

    @staticmethod
    def _encoding_array(encoding: str) -> Result[np.ndarray, str]:
        """
        Converte string serializada para np.ndarray.
        """
        return FaceModel._validate_encoding(encoding)

    # ------------------------
    # SERIALIZAÇÃO
    # ------------------------

    def to_map(
        self, model: Optional["FaceModel"] = None, as_string: bool = False
    ) -> Result[dict, str]:
        """
        Converte o modelo para dict.
        - Se as_string=True → encodings como string serializada.
        - Se False → encodings como lista ou np.ndarray.
        """
        try:
            target = model or self
            if as_string:
                enc_res = self._encoding_string(target.encodings)
                if enc_res.is_failure:
                    return enc_res
                encodings_out = enc_res.value
            else:
                encodings_out = (
                    target.encodings.tolist()
                    if isinstance(target.encodings, np.ndarray)
                    else target.encodings
                )

            return Success(
                {
                    "encodings": encodings_out,
                    "location": target.location,
                },
                log="FaceModel convertido para dict",
                details=f"Encodings serializado como {'string' if as_string else 'lista'}",
            )
        except Exception as e:
            return Failure("Erro ao converter FaceModel para dict", details=str(e))
