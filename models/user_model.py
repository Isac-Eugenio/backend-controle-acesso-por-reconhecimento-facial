from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, PrivateAttr, field_validator
from typing import Optional, Literal, Union, List
import numpy as np
from core.commands.result import Result, Success, Failure
from models.face_model import FaceModel
from core.utils.api_utils import ApiUtils

generate_id = ApiUtils._generate_id()


class PermissionEnum(str, Enum):
    """
    Enum que define os níveis de permissão de um usuário:
    - DISCENTE: aluno ou estudante
    - DOCENTE: professor ou instrutor
    - ADMINISTRADOR: usuário com privilégios administrativos
    """

    DISCENTE = "discente"
    DOCENTE = "docente"
    ADMINISTRADOR = "administrador"


class UserModel(BaseModel):
    """
    Modelo que descreve um usuário no sistema.
    - Pode representar discentes, docentes e administradores.
    - Contém dados pessoais, permissões e encodings faciais para autenticação.
    """

    id: str = Field(default_factory=ApiUtils._generate_id, max_length=8)
    nome: Optional[str] = Field(None, max_length=100)
    alias: Optional[str] = Field(None, max_length=11)
    cpf: Optional[str] = Field(None, max_length=14)
    email: Optional[EmailStr] = Field(None, max_length=255)
    matricula: Optional[str] = Field(None, max_length=255)
    senha: Optional[str] = Field(None, max_length=64)
    icon_path: Optional[str] = Field(None, max_length=255)

    permission_level: PermissionEnum = Field(default=PermissionEnum.DISCENTE)

    encodings: Optional[str] = None

    _face_model: FaceModel = PrivateAttr(default_factory=FaceModel)

    # Se senha não estiver em hash SHA256, gera o hash
    @field_validator("senha", mode="before")
    def hash_senha(cls, v):
        if v is None:
            return None
        if ApiUtils._is_sha256_hash(v):
            return v
        return ApiUtils._hash_sha256(v)

    @property
    def senha(self):
        return self.senha

    # Atualiza senha; garante SHA256
    @senha.setter
    def senha(self, value: str):
        if value is None:
            self._senha = None
        elif ApiUtils._is_sha256_hash(value):
            self._senha = value
        else:
            self._senha = ApiUtils._hash_sha256(value)

    def set_encoding(
        self, encoding: Union[str, np.ndarray, List[float]]
    ) -> Result[np.ndarray, str]:
        """
        Converte string/lista para np.ndarray e valida tamanho
        Atualiza FaceModel e salva string no campo encodings
        """
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
                return Failure("Encoding deve ser um np.ndarray, lista ou string")

            if encoding.dtype.kind not in ("f", "i"):
                return Failure("Encoding deve ser numérico (float ou int)")

            if encoding.size != 128:
                return Failure("Encoding deve conter exatamente 128 valores")

            # Atualiza FaceModel
            self._face_model.encodings = encoding

            # Gera string a partir do encoding
            str_res = self._face_model._encoding_string(encoding)
            if str_res.is_failure:
                return str_res

            # Salva string no campo do modelo
            self.encodings = str_res.value

            return Success(
                encoding,
                log="Encoding atualizado com sucesso",
                details=f"Tamanho: {encoding.size}",
            )

        except Exception as e:
            return Failure(f"Erro ao definir encoding", details=str(e))

    @classmethod
    def from_map(cls, data: dict) -> Result["UserModel", str]:
        # Cria instância de UserModel a partir de dicionário
        # Se houver encoding, seta no FaceModel
        try:
            # Cria a instância do modelo
            user = cls(
                id=data.get("id", ApiUtils._generate_id()),
                nome=data.get("nome", ""),
                alias=data.get("alias", ""),
                cpf=data.get("cpf", ""),
                email=data.get("email", ""),
                matricula=data.get("matricula"),
                senha=data.get("senha"),
                icon_path=data.get("icon_path"),
                permission_level=data.get("permission_level", "discente"),
            )

            # Se houver encoding no map, seta no FaceModel
            encoding = data.get("encodings")
            if encoding:
                set_res = user.set_encoding(encoding)
                if set_res.is_failure:
                    return Failure(f"Erro ao processar encoding", details=str(e))

            return Success(user, log="BaseUserModel criado a partir do map com sucesso")

        except Exception as e:
            return Failure(
                f"Erro ao criar BaseUserModel a partir do map", details=str(e)
            )

    def to_map(self) -> Result[dict, str]:
        # Converte o UserModel para dict
        # Encodings são serializados em string
        try:
            # Converte o encoding para string via FaceModel
            encoding_str = None
            if (
                self._face_model.encodings is not None
                and len(self._face_model.encodings) > 0
            ):
                enc_res = self._face_model._encoding_string(self._face_model.encodings)
                if enc_res.is_failure:
                    return enc_res
                encoding_str = enc_res.value

            # Cria o dict com todos os campos
            data_map = {
                "id": self.id,
                "nome": self.nome,
                "alias": self.alias,
                "cpf": self.cpf,
                "email": self.email,
                "matricula": self.matricula,
                "senha": self.senha,
                "icon_path": self.icon_path,
                "permission_level": self.permission_level,
                "encodings": encoding_str,
            }

            return Success(
                data_map, log="BaseUserModel convertido para map com sucesso"
            )

        except Exception as e:
            return Failure(f"Erro ao converter BaseUserModel para map", details=str(e))
