from typing import Any, AsyncGenerator
from core.commands.result import *
from models.historic_model import HistoricModel
from models.login_model import LoginModel
from models.perfil_model import PerfilModel
from models.user_model import UserModel
from repository.api_repository import ApiRepository
from services.face_service import FaceService


class ApiController:
    """
    Controller principal para a API, responsável por:
    - Gerenciar usuários (login, registro, atualização, exclusão)
    - Validar permissões administrativas
    - Registrar ações de usuários no histórico
    - Integrar com o repositório de face para coleta de rostos
    """

    def __init__(self, api_repository: ApiRepository, face_service: FaceService):
        """
        Inicializa o controller com:
        - api_repository: interface para operações de banco de dados
        - face_service: serviço para captura e processamento de rostos
        """
        self.api_repository = api_repository
        self.face_service = face_service

    async def register_user_db(
        self, user_data: UserModel, admin_key_access: LoginModel
    ) -> AsyncGenerator[Result[Any, str], None]:
        """
        Registra um novo usuário no banco de dados.
        - Valida se o usuário que está tentando registrar é admin.
        - Coleta o encoding facial do usuário via FaceService.
        - Insere o usuário no banco.
        - Registra ação no histórico.
        - Retorna resultados intermediários via AsyncGenerator (Running, Failure, Success).
        """
        yield Running("Iniciando registro ...")

        # Valida ID do usuário administrador
        is_admin = await self.api_repository.user_is_admin(user_data=admin_key_access)
        if is_admin.is_failure:
            yield Failure("Acesso Negado ao Usuario!", details=is_admin.value)
            return

        if not is_admin.value:
            yield Failure("Acesso Negado ao Usuario!", details=is_admin.value)
            return

        yield Running("iniciando Coleta do rosto ...")
        # Coleta encoding do rosto do usuário
        get_encoding = await self.face_service.get_first_face_encoding_async()
        if get_encoding.is_failure:
            yield Failure("Erro ao coletar o rosto", details=get_encoding.value)
            return

        # Associa encoding facial ao usuário
        user_data.set_encoding(get_encoding.value)
        yield Running("Rosto coletado com sucesso")

        # Insere usuário no banco de dados
        db_result = await self.api_repository.insert_user_table(user_data)
        if db_result.is_failure:
            yield Failure("erro ao registrar o usuario ...", details=db_result.value)
            return

        # Registra ação no histórico de admin
        db_result_his = await self.api_repository.find_user(admin_key_access)
        if db_result_his.is_failure:
            yield Failure(
                "Erro ao registrar o historico ...", details=db_result_his.value
            )
            return

        historic_model = HistoricModel(**dict(db_result_his.value))
        result_his = await self.register_historic_from_model(
            historic_model, f"registrou o novo usuario {user_data.alias} !"
        )

        if result_his.is_failure:
            yield Failure("Erro ao registrar o historico ...", details=result_his.value)
            return

        # Retorna sucesso final
        yield Success("Usuario registrado com sucesso ...", details=db_result.value)

    async def get_user_table(self) -> Result[list[PerfilModel], str]:
        """
        Retorna a tabela completa de usuários.
        - Consulta o repositório.
        - Em caso de falha, retorna Failure.
        """
        result = await self.api_repository.select_user_table()
        if result.is_failure:
            return Failure(
                "Erro ao coletar tabela de usuarios ...", details=result.value
            )

        return Success(result.value, log=result.log)

    async def login(self, login_data: dict) -> Result[PerfilModel, str]:
        """
        Valida login de usuário.
        - Converte dados do login para LoginModel.
        - Busca usuário no repositório.
        - Retorna Success se autorizado, Failure se não autorizado.
        """
        login_data = LoginModel(**login_data)
        result = await self.api_repository.find_user(login_data)
        if result.is_failure:
            if result.log is None:
                return Failure("Erro ao Autorizar o login ...", details=result.value)
            return Failure("Usuario não Autorizado...", log=result.log)

        # Retorna usuário como PerfilModel
        return Success(PerfilModel(**dict(result.value)), log="Usuario Autorizado ...")

    async def isAdmin(self, admin_data: LoginModel) -> Result[bool, str]:
        """
        Verifica se o usuário possui privilégios de administrador.
        - Retorna Success(True) se for admin.
        - Retorna Failure se não for ou houver erro.
        """
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
        """
        Busca um usuário específico.
        - Valida se admin_data tem permissões de admin.
        - Retorna PerfilModel do usuário encontrado.
        """
        user_data = UserModel(**user_data)
        admin_data = LoginModel(**admin_data)

        auth = await self.isAdmin(admin_data)
        if not auth.value:
            return Failure("Usuario não autorizado", details=auth.value)

        result = await self.api_repository.find_user(user_data)
        if result.is_failure:
            return Failure("Erro ao encontrar usuario ...", details=result.value)

        return Success(
            PerfilModel(**dict(result.value)), log="Usuario encontrado com sucesso ..."
        )

    async def delete_user(self, user_data: dict, admin_data: dict) -> Result[None, str]:
        """
        Deleta um usuário do banco.
        - Valida admin antes da exclusão.
        - Retorna Success se deletado ou Failure se erro.
        """
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
        """
        Atualiza dados de um usuário.
        - Verifica permissões de admin.
        - Atualiza no banco de dados.
        - Retorna Success ou Failure.
        """
        user_data = UserModel(**user_data)
        admin_data = LoginModel(**admin_data)
        new_data = UserModel(**new_data)

        auth = await self.isAdmin(admin_data)
        if not auth.value:
            return Failure("Usuario não autorizado", details=auth.value)

        result = await self.api_repository.update_user_table(user_data, new_data)
        if result.is_failure:
            return Failure("Erro ao atualizar usuario ...", details=result.value)

        return Success(None, log="Usuario atualizado com sucesso ...")

    async def register_historic(self, historic_data: HistoricModel) -> Result[Any, str]:
        """
        Registra uma ação no histórico do sistema.
        - Recebe um HistoricModel.
        - Retorna Success ou Failure.
        """
        result = await self.api_repository.insert_historic_table(historic_data)
        if result.is_failure:
            return Failure(
                "Erro ao registrar historico", details=result.value, error=True
            )

        return Success(result.value, log="Historico registrado com sucesso")

    async def register_historic_from_model(self, model: HistoricModel, action: str):
        """
        Registra histórico a partir de um modelo e ação.
        - Adiciona log detalhado à ação do usuário.
        - Chama register_historic internamente.
        """
        model.set_log(f"Usuario {model.alias} {action}!")
        return await self.register_historic(model)
