from typing import List, Optional, Union
import numpy as np
from pydantic import BaseModel, EmailStr, Field
from core.commands.result import *
from models.user_model import UserModel, PermissionEnum


class PerfilModel(BaseModel):
    id: str
    nome: Optional[str] = Field(None, max_length=100)
    alias: Optional[str] = Field(None, max_length=11)
    email: Optional[EmailStr] = Field(None, max_length=255)
    matricula: Optional[str] = Field(None, max_length=255)
    icon_path: Optional[str] = Field(None, max_length=255)
    permission_level: PermissionEnum = PermissionEnum.DISCENTE
    encodings: Union[List[float], Optional[str]] = Field(None)

    @classmethod
    def from_user(cls, user: UserModel) -> "PerfilModel":
        # Retorna apenas dados seguros (sem cpf, senha, encodings, etc.)
        return cls(
            id=user.id,
            nome=user.nome,
            alias=user.alias,
            email=user.email,
            matricula=user.matricula,
            icon_path=user.icon_path,
            permission_level=user.permission_level,
        )

    def set_encoding(
        self, encoding: Union[str, np.ndarray, List[float]]
    ) -> Result[np.ndarray, str]:
        try:
            # Converte string para np.ndarray
            if isinstance(encoding, str):
                enc_res = self._face_model._encoding_array(encoding)
                if enc_res.is_failure:
                    return enc_res
                encoding = enc_res.value

            # Converte lista para np.ndarray
            elif isinstance(encoding, list):
                encoding = np.array(encoding, dtype=float)

            # Verifica tipo
            if not isinstance(encoding, np.ndarray):
                return Failure("Encoding deve ser np.ndarray, lista ou string")

            if encoding.dtype.kind not in ("f", "i"):
                return Failure("Encoding deve ser numérico (float ou int)")

            if encoding.size != 128:
                return Failure("Encoding deve conter exatamente 128 valores")

            # Atualiza FaceModel para cálculos
            self._face_model.encodings = encoding

            # Salva como lista no campo do modelo (JSON-friendly)
            self.encodings = encoding.tolist()

            return Success(
                encoding,
                log="Encoding atualizado",
                details=f"Tamanho: {encoding.size}",
            )

        except Exception as e:
            return Failure("Erro ao definir encoding", details=str(e))
