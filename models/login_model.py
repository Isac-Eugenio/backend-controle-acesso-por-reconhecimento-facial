from typing import Union
from pydantic import BaseModel, EmailStr, model_serializer
from core.utils.api_utils import ApiUtils
from models.user_model import PermissionEnum, UserModel


class LoginModel(BaseModel):
    """
    Modelo que representa os dados de login de um usuário no sistema de controle de acesso.

    Este modelo é usado para autenticação, verificando credenciais (email e senha)
    e nível de permissão do usuário.

    Campos principais:
        - email: email do usuário, validado automaticamente pelo Pydantic.
        - senha: senha do usuário, armazenada ou enviada em formato hash (SHA256 recomendado).
        - permission_level: nível de permissão exigido para o login (ADMINISTRADOR por padrão).

    Funcionalidades:
        - from_user(): cria um LoginModel a partir de um objeto UserModel,
          extraindo email e senha automaticamente.
        - serialize(): retorna um dicionário com email e senha hash, pronto para
          envio ou armazenamento seguro. A senha é criptografada usando SHA256
          via ApiUtils._hash_sha256.
    
    Observação:
        Este modelo não armazena a senha em texto puro para segurança.
        É útil tanto para validação de login em endpoints quanto para autenticação
        interna entre módulos do sistema.
    """

    email: EmailStr
    senha: str
    permission_level: PermissionEnum = PermissionEnum.ADMINISTRADOR

    @classmethod
    def from_user(cls, user: UserModel) -> "LoginModel":
        """Cria um LoginModel a partir de um UserModel existente"""
        return cls(email=user.email, senha=user.senha)

    @model_serializer
    def serialize(self) -> dict:
        """Serializa os dados de login, retornando a senha como hash SHA256"""
        return {"email": self.email, "senha": ApiUtils._hash_sha256(self.senha)}
