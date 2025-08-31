from typing import AsyncGenerator, List, Union

from numpy import record
from core.commands.result import Failure, Result, Running, Success
from core.config.app_config import DatabaseTables
from core.utils.api_utils import ApiUtils
from models.device_model import DeviceModel
from models.face_model import FaceModel
from models.historic_model import HistoricModel
from models.login_model import LoginModel
from models.perfil_model import PerfilModel
from models.query_model import QueryModel
from models.user_model import UserModel, PermissionEnum
from repository.database_repository import DatabaseRepository
from repository.face_repository import FaceRepository
from services.face_service import FaceService


class ApiRepository:
    def __init__(
        self, db_repository: DatabaseRepository, face_repository: FaceRepository
    ):
        self.db = db_repository
        self.face_repository = face_repository

    async def select_user_table(self) -> Result[List[PerfilModel], str]:
        query = QueryModel(table=DatabaseTables.perfis)

        result = await self.db.select(query)

        if result.is_failure:
            return Failure("Erro ao coletar tabela de usuários", details=result.value)

        filtered_result = []
        for record in result.value:
            dict_t = dict(record)
            perfil = PerfilModel(**dict_t)
            filtered_result.append(perfil)

        return Success(filtered_result, log="Tabela de usuários coletada com sucesso")

    async def insert_user_table(self, user_data: UserModel) -> Result[str, str]:

        user_data_dict = user_data.model_dump()

        query = QueryModel(table=DatabaseTables.perfis, values=user_data_dict)

        result = await self.db.insert(query)

        if result.is_failure:
            return Failure("Erro ao inserir usuário", details=result.value)

        return Success(result.value, log="Usuário inserido com sucesso")

    async def update_user_table(
        self, user_data: UserModel, new_user_data: UserModel
    ) -> Result[str, str]:
        user_data_dict = user_data.model_dump(exclude_none=True, exclude_unset=True)
        new_user_data_dict = new_user_data.model_dump(
            exclude_none=True, exclude_unset=True
        )

        query = QueryModel(table=DatabaseTables.perfis, values=user_data_dict)
        new_query = QueryModel(table=DatabaseTables.perfis, values=new_user_data_dict)

        result = await self.db.update(query=query, new_query=new_query)
        
        if result.is_failure:
            return Failure("Erro ao atualizar usuário", details=result.value)

        if result.value == 0:
            return Failure("Nenhum foi usuário atualizado", details=result.value)

        if result.value >= 2:
            return Failure("Mais de um usuário foi atualizado", details=result.value)

        return Success(result.value, log="Usuário atualizado com sucesso")

    async def delete_user_table(self, user_data: UserModel) -> Result[str, str]:
        query = QueryModel(
            table=DatabaseTables.perfis, values=user_data.model_dump(exclude_unset=True)
        )

        result = await self.db.delete(query)

        if result.is_failure:
            return Failure("Erro ao deletar usuário", details=result.value)

        return Success(result.value, log="Usuário deletado com sucesso")

    async def find_user(
        self, user_data: Union[PerfilModel, UserModel, LoginModel]
    ) -> Result[PerfilModel, str]:
        user_data_dict = user_data.model_dump(exclude_none=True, exclude_unset=True)

        if not user_data_dict:
            return Failure("Erro ao ler dados do request")

        query = QueryModel(table=DatabaseTables.perfis, values=user_data_dict)

        result = await self.db.select_one(query)

        if result.is_failure:
            return Failure("Erro ao encontrar usuário", details=result.value)

        if result.value is None:
            return Failure("Usuário não encontrado", log=result.log)
        return Success(_value=result.value, log="Usuário encontrado com sucesso")

    async def user_is_admin(self, user_data: UserModel) -> Result[bool, str]:

        user_data.permission_level = PermissionEnum.ADMINISTRADOR

        user_data_dict = user_data.model_dump(exclude_none=True, exclude_unset=True)

        query = QueryModel(table=DatabaseTables.perfis, values=user_data_dict)

        result = await self.db.count(query)

        if result.is_failure:
            return Failure(
                "Erro ao verificar permissões do usuário", details=result.value
            )

        dict_count_result = dict(result.value)

        if dict_count_result.get("total") > 0:
            return Success(True, log="Usuário é um administrador")

        return Success(
            False,
            log="Usuario não é um administrador",
        )

    async def open_door(self, device_data: DeviceModel) -> Result[any, str]:
        device_data_dict = device_data.model_dump(exclude_none=True, exclude_unset=True)

        if not device_data_dict:
            return Failure(
                "Erro ao ler dados do dispositivo",
                log="Erro Device",
                details="Dados do dispositivo inválidos",
                error=True,
            )

        query = QueryModel(table=DatabaseTables.dispositivos, values=device_data_dict)
        result = await self.db.select(query)

        if result.is_failure:
            return Failure(
                "Erro ao buscar dispositivo",
                log="Erro Device",
                details=result.value,
                error=True,
            )

        res = result.value
        devices: list[DeviceModel] = [DeviceModel(**dict(i)) for i in res]

        columns = PerfilModel.model_fields.keys()
        query = QueryModel(table=DatabaseTables.perfis, columns=list(columns))
        result = await self.db.select(query)
        if result.is_failure:
            return Failure(
                "Erro ao encontrar perfis",
                log="Erro Perfis",
                details=result.value,
                error=True,
            )

        profiles: list[PerfilModel] = []
        for i in result.value:
            perfil = PerfilModel(**dict(i))
            res = self.face_repository.face_model._encoding_array(perfil.encodings)

            if res.is_failure:
                return Failure(
                    "Erro ao processar encodings do perfil",
                    log="Erro Encode",
                    details=res.value,
                    error=True,
                )

            perfil.encodings = res.value if res.is_success else perfil.encodings
            profiles.append(perfil)

        face_to_compare = (
            await self.face_repository.face_service.get_first_face_encoding_async()
        )
        if face_to_compare.is_failure:
            return Failure(
                "Erro ao obter rosto para comparação",
                log="Erro Face",
                details=face_to_compare.value,
                error=True,
            )

        match = await self.face_repository.match_face_to_profiles_async(
            profiles, face_to_compare.value
        )
        if match.is_failure:
            if match.error:
                return Failure(
                    "Erro ao comparar rosto com perfis",
                    log="Erro Match",
                    details=match.value,
                    error=True,
                )

            return Failure(
                "Rosto não reconhecido",
                log="Acesso Negado",
                details=match.value,
                error=False,
            )

        # Nenhum perfil correspondeu -> apenas acesso negado, não é "erro de execução"
        if not match.value:
            return Failure(
                "Acesso negado: rosto não autorizado",
                log="Acesso Negado",
                details="Nenhum perfil corresponde ao rosto detectado",
            )

        match.value.encodings = None

        return Success(
            match.value.model_dump(),
            log="Porta Aberta",
            details="Rosto reconhecido e comparado com sucesso",
        )

    async def insert_historic_table(self, historic_data: HistoricModel) -> Result[any, str]:
        historic_data_dict = historic_data.model_dump(exclude_none=True, exclude_unset=True)

        query = QueryModel(table=DatabaseTables.historico, values=historic_data_dict)
        result = await self.db.insert(query)

        print(result)

        if result.is_failure:
            return Failure(
                "Erro ao inserir histórico",
                log="Erro Historico",
                details=result.value,
                error=True,
            )

        return Success(
            result.value,
            log="Histórico inserido com sucesso",
            details="Registro de acesso criado",
        )