from typing import List, Optional, Union
import numpy as np
from pydantic import BaseModel, EmailStr, Field
from core.commands.result import *
from models.user_model import UserModel, PermissionEnum


class PerfilModel(BaseModel):
    """
    Modelo que representa o perfil de um usuário no sistema de controle de acesso.

    Este modelo é usado para exibir ou manipular informações seguras do usuário,
    sem expor dados sensíveis como CPF ou senha, sendo adequado para dashboards,
    APIs internas ou exportação de dados.

    Campos principais:
        - id: identificador único do usuário.
        - nome, alias, email, matricula, icon_path: informações básicas do perfil.
        - permission_level: nível de acesso do usuário (discente, docente, administrador).
        - encodings: vetor de características faciais (128 floats) para reconhecimento
          facial. Pode ser armazenado como lista ou string (serializável).

    Funcionalidades:
        - from_user(): cria um PerfilModel a partir de um UserModel existente,
          mantendo apenas dados seguros e descartando informações sensíveis.
        - set_encoding(): define ou atualiza os encodings faciais do perfil,
          convertendo strings ou listas para np.ndarray e validando o tamanho
          (128 valores). Atualiza tanto o atributo interno da FaceModel quanto
          o campo encodings do modelo (JSON-friendly).

    Observações:
        - Os encodings são usados para reconhecimento facial e devem ter exatamente
          128 valores numéricos (float ou int).
        - Erros na conversão ou validação retornam um objeto Failure detalhando o problema.
        - Operações bem-sucedidas retornam um objeto Success com log e detalhes do encoding.
    """

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
        """Retorna um PerfilModel seguro, sem dados sensíveis"""
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
        """
        Define o encoding facial do usuário, convertendo e validando os dados.

        Parâmetros:
            - encoding: pode ser string, lista ou np.ndarray.

        Retorna:
            - Success com o np.ndarray validado e detalhes do tamanho do encoding.
            - Failure se houver erro na conversão, validação ou tipo inválido.
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
