from typing import Union
from pydantic import BaseModel, EmailStr, model_serializer
from core.utils.api_utils import ApiUtils
from models.user_model import PermissionEnum, UserModel


class LoginModel(BaseModel):
    email: EmailStr
    senha: str
    permission_level: PermissionEnum = PermissionEnum.ADMINISTRADOR

    @classmethod
    def from_user(cls, user: UserModel) -> "LoginModel":
        return cls(email=user.email, senha=user.senha)

    @model_serializer
    def serialize(self) -> dict:
        return {"email": self.email, "senha": ApiUtils._hash_sha256(self.senha)}
