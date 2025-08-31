from typing import Any, AsyncGenerator
from core.commands.result import *
from core.utils.api_utils import ApiUtils
from models import historic_model
from models.historic_model import HistoricModel
from models.login_model import LoginModel
from models.perfil_model import PerfilModel
from models.user_model import UserModel
from repository.api_repository import ApiRepository
from services.face_service import FaceService


class ApiController:
    def __init__(self, api_repository: ApiRepository, face_service: FaceService):
        self.api_repository = api_repository
        self.face_service = face_service

    async def register_user_db(
        self, user_data: UserModel, admin_key_access: LoginModel
    ) -> AsyncGenerator[Result[Any, str], None]:
        yield Running("Iniciando registro ...")

        admin_key_access_dict = admin_key_access.model_dump(
            exclude_none=True, exclude_unset=True
        )
        yield Running("Verificando ID do usuario ...")

        is_admin = await self.api_repository.user_is_admin(user_data=admin_key_access)
        if is_admin.is_failure:
            yield Failure("Acesso Negado ao Usuario!", details=is_admin.value)
            return

        if is_admin.is_success:
            if is_admin.value:
                yield Running("Usuario Autorizado ...")

            else:
                yield Failure("Acesso Negado ao Usuario!", details=is_admin.value)
                return

        yield Running("iniciando Coleta do rosto ...")

        get_encoding = await self.face_service.get_first_face_encoding_async()

        if get_encoding.is_failure:
            yield Failure("Erro ao coletar o rosto", details=get_encoding.value)
            return

        face_encoding = get_encoding.value

        user_data.set_encoding(face_encoding)

        yield Running("Rosto coletado com sucesso")

        yield Running("Iniciando registro do usuario no banco de dados ...")

        db_result = await self.api_repository.insert_user_table(user_data)

        if db_result.is_failure:
            yield Failure("erro ao registrar o usuario ...", details=db_result.value)
            return

        db_result_his = await self.api_repository.find_user(admin_key_access)

        if db_result_his.is_failure:
            yield Failure(
                "Erro ao registrar o historico ...", details=db_result_his.value
            )
            return

        admin_data_dict = dict(db_result_his.value)

        historic_model = HistoricModel(**admin_data_dict)

        result_his = await self.register_historic_from_model(
            historic_model, f"registrou o novo usuario {user_data.alias} !"
        )

        if result_his.is_failure:
            yield Failure("Erro ao registrar o historico ...", details=result_his.value)
            return

        yield Success("Usuario registrado com sucesso ...", details=db_result.value)

    async def get_user_table(self) -> Result[list[PerfilModel], str]:
        result = await self.api_repository.select_user_table()
        if result.is_failure:
            return Failure(
                "Erro ao coletar tabela de usuarios ...", details=result.value
            )

        return Success(result.value, log=result.log)

    async def login(self, login_data: dict) -> Result[PerfilModel, str]:

        login_data = LoginModel(**login_data)

        result = await self.api_repository.find_user(login_data)

        if result.is_failure:
            if result.log is None:
                return Failure("Erro ao Autorizar o login ...", details=result.value)

            return Failure("Usuario não Autorizado...", log=result.log)

        result_dict = dict(result.value)

        teste = PerfilModel(**result_dict)

        return Success(teste, log="Usuario Autorizado ...")

    async def isAdmin(self, admin_data: LoginModel) -> Result[bool, str]:

        result = await self.api_repository.user_is_admin(admin_data)

        if result.is_failure:
            return Failure(
                "Erro ao verificar se o usuario é admin ...", details=result.value
            )

        if result.value:
            return Success(result.value, log="Usuario autorizado ...")

        return Failure(result.value, log="Usuario não autorizado ...")

    async def find_user(
        self, user_data: dict, admin_data: dict
    ) -> Result[PerfilModel, str]:

        user_data = UserModel(**user_data)

        admin_data = LoginModel(**admin_data)

        auth = await self.isAdmin(admin_data)

        result = await self.api_repository.find_user(user_data)

        if not auth.value:
            return Failure("Usuario não autorizado", details=auth.value)

        if result.is_failure:
            return Failure("Erro ao encontrar usuario ...", details=result.value)

        result_value_dict = dict(result.value)

        result_perfil_model = PerfilModel(**result_value_dict)

        return Success(result_perfil_model, log="Usuario encontrado com sucesso ...")

    async def delete_user(self, user_data: dict, admin_data: dict) -> Result[None, str]:
        user_data = UserModel(**user_data)
        admin_data = LoginModel(**admin_data)

        auth = await self.isAdmin(admin_data)

        if not auth.value:
            return Failure("Usuario não autorizado", details=auth.value)

        result = await self.api_repository.delete_user_table(user_data)

        if result.is_failure:
            return Failure("Erro ao deletar usuario ...", details=result.value)

        return Success(None, log="Usuario deletado com sucesso ...")

    async def update_user(
        self, user_data: dict, new_data: dict, admin_data: dict
    ) -> Result[None, str]:
        user_data = UserModel(**user_data)
        admin_data = LoginModel(**admin_data)
        new_data = UserModel(**new_data)

        auth = await self.isAdmin(admin_data)

        if not auth.value:
            return Failure("Usuario não autorizado", details=auth.value)

        result = await self.api_repository.update_user_table(user_data, new_data)

        print(result)

        if result.is_failure:
            return Failure("Erro ao atualizar usuario ...", details=result.value)

        return Success(None, log="Usuario atualizado com sucesso ...")

    async def register_historic(self, historic_data: HistoricModel) -> Result[any, str]:
        result = await self.api_repository.insert_historic_table(historic_data)

        if result.is_failure:
            return Failure(
                "Erro ao registrar historico", details=result.value, error=True
            )

        return Success(result.value, log="Historico registrado com sucesso")

    async def register_historic_from_model(self, model: HistoricModel, action: str):

        model.set_log(f"Usuario {model.alias} {action}!")

        result_his = await self.register_historic(model)

        return result_his
