from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi import FastAPI
import asyncio
import json
from fastapi.responses import JSONResponse, StreamingResponse

# Importa controladores, comandos, modelos e repositórios do sistema
from controllers.api_controller import ApiController
from core.commands.async_command import AsyncCommand
from core.commands.stream_command import StreamCommand
from core.config.app_config import CameraConfig, DatabaseTables
from models.device_model import DeviceModel
from models.face_model import FaceModel
from models.historic_model import HistoricModel
from models.login_model import LoginModel
from models.perfil_model import PerfilModel
from models.stream_response_model import StreamResponse
from models.user_model import UserModel
from repository.api_repository import ApiRepository
from repository.camera_repository import CameraRepository
from repository.database_repository import DatabaseRepository
from repository.face_repository import FaceRepository
from services.face_service import FaceService
from models.response_model import Response

# -------------------------------
# Instanciação dos repositórios e serviços
# -------------------------------
camera_repository = CameraRepository(CameraConfig())  # Controle da câmera
db_repository = DatabaseRepository()  # Acesso ao banco de dados
face_service = FaceService(camera_repository)  # Serviço de reconhecimento facial
face_model = FaceModel()  # Modelo de dados de rosto
face_repository = FaceRepository(face_service, face_model)  # Repositório para rostos
api_repository = ApiRepository(db_repository, face_repository)  # API de persistência
api = ApiController(api_repository, face_service)  # Controller principal
app = FastAPI()  # Cria a aplicação FastAPI

# -------------------------------
# Middleware CORS
# -------------------------------
# Permite que a API aceite requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Qualquer domínio
    allow_credentials=True,
    allow_methods=["*"],  # Todos os métodos HTTP
    allow_headers=["*"],  # Todos os headers
)


# -------------------------------
# Rota de login
# -------------------------------
@app.post("/login")
async def login(request: Request):
    form = await request.json()  # Captura os dados JSON do request
    result = await api.login(form)  # Chama o método de login no controller

    if result.is_success:  # Se login bem-sucedido
        data_dict = result.value.model_dump()  # Converte objeto em dict
        response = Response(
            log="Login realizado com sucesso ...",
            data=data_dict,
            code=200,
        )

        # Cria registro histórico do login
        historic_model = HistoricModel(**data_dict)
        result_his = await api.register_historic_from_model(
            historic_model, "logou no sistema !"
        )

        if result_his.is_failure:  # Se houver erro ao registrar histórico
            response = Response(
                log="Erro ao realizar login ..",
                details=result_his.details,
                error=result_his.value,
                code=500,
            )
            return response.json()

        return response.json()  # Retorna resposta de sucesso

    # Caso login falhe
    if result.is_failure:
        if result.details is None:
            response = Response(log="Acesso Negado ...", code=401)
            return response.json()

        response = Response(
            log="Erro ao realizar login ..",
            details=result.details,
            error=result.value,
            code=500,
        )
        return response.json()


# -------------------------------
# Rota de logout
# -------------------------------
@app.post("/logout")
async def logout(request: Request):
    form = await request.json()  # Captura dados do request
    perfil = PerfilModel(**form)  # Cria modelo do usuário
    perfil_dict = perfil.model_dump()
    historic_model = HistoricModel(**perfil_dict)
    historic_model.set_log(f"Usuario {perfil.alias} deslogou no sistema !")

    # Registra histórico
    result_his = await api.register_historic_from_model(
        historic_model, "deslogou no sistema !"
    )

    if result_his.is_failure:  # Se houver falha
        response = Response(
            log="Erro ao registrar logout..",
            details=result_his.details,
            error=result_his.value,
            code=500,
        )
        return response.json()

    # Logout bem sucedido
    response = Response(
        log="logout bem sucedido ...",
        details=result_his.details,
        code=200,
    )
    return response.json()


# -------------------------------
# Rota para consultar tabela de perfis
# -------------------------------
@app.post("/perfis")
async def table_perfil(request: Request):
    form = await request.json()
    model = LoginModel(**form)
    auth = await api.isAdmin(model)  # Verifica se usuário é admin

    if auth.value:  # Admin autorizado
        result = await api.get_user_table()  # Pega tabela de usuários
        user_login = await api.login(form)  # Registra login
        if result.is_failure:
            response = Response(code=500, log=result.value, details=result.details)
            return response.json()

        perfil_auth_dict = user_login.value.model_dump()
        historic_model = HistoricModel(**perfil_auth_dict)

        # Registra histórico da ação
        result_his = await api.register_historic_from_model(
            historic_model, "consultou a tabela de usuarios"
        )

        if result_his.is_failure:
            response = Response(
                code=500, log=result_his.value, details=result_his.details
            )
            return response.json()

        response = Response(code=200, data=result.value, log=result.log)
        return response.json()

    # Falha na autorização
    if auth.is_failure:
        response = Response(code=403, log=auth.log, details=auth.details)
        return response.json()

    response = Response(code=401, log="Acesso Negado ...", details=auth.log)
    return response.json()


# -------------------------------
# Rota para registrar usuário
# -------------------------------
@app.post("/register_user")
async def register_user(request: Request):
    form = await request.json()
    user_data = form.get("user", {})
    admin_access = form.get("admin", {})
    user_model = UserModel(**user_data)
    login_model = LoginModel(**admin_access)

    # Comando de registro em streaming
    command = StreamCommand(lambda: api.register_user_db(user_model, login_model))
    stream = StreamResponse(command)
    return await stream.response()


# -------------------------------
# Rota para buscar usuário
# -------------------------------
@app.post("/find_user")
async def find_user(request: Request):
    form = await request.json()
    user_data = form.get("user", {})
    admin_data = form.get("admin", {})

    # Executa comando assíncrono para buscar usuário
    command = AsyncCommand(lambda: api.find_user(user_data, admin_data))
    result = await command.execute_async()

    if result.is_failure:  # Falha na busca
        response = Response(code=500, log=result.value, details=result.details)
        return response.json()

    # Registra histórico da ação
    historic_model = HistoricModel(**admin_data)
    result_his = await api.register_historic_from_model(
        historic_model, f"consultou dados do usuario {result.value.alias} !"
    )

    if result_his.is_failure:
        response = Response(code=500, log=result_his.value, details=result_his.details)
        return response.json()

    response = Response(code=200, data=result.value, log=result.log)
    return response.json()


# -------------------------------
# Rota para deletar usuário
# -------------------------------
@app.post("/delete_user")
async def delete_user(request: Request):
    form = await request.json()
    user_data = form.get("user", {})
    admin_data = form.get("admin", {})

    command = AsyncCommand(lambda: api.delete_user(user_data, admin_data))
    result = await command.execute_async()

    if result.is_failure:
        response = Response(code=500, log=result.value, details=result.details)
        return response.json()

    # Registra histórico do delete
    historic_model = HistoricModel(**admin_data)
    result_his = await api.register_historic_from_model(
        historic_model, f"deletou o usuario {user_data.get('alias', '')} !"
    )

    if result_his.is_failure:
        response = Response(code=500, log=result_his.value, details=result_his.details)
        return response.json()

    response = Response(code=200, data=result.value, log=result.log)
    return response.json()


# -------------------------------
# Rota para atualizar usuário
# -------------------------------
@app.post("/update_user")
async def update_user(request: Request):
    form = await request.json()
    user_data = form.get("user", {})
    admin_data = form.get("admin", {})
    new_data = form.get("new_data", {})

    # Executa comando assíncrono para update
    command = AsyncCommand(lambda: api.update_user(user_data, new_data, admin_data))
    result = await command.execute_async()

    # Cria histórico
    historic_model = HistoricModel(**admin_data)
    keys = list(new_data.keys())
    if len(keys) == 1:
        frase = f"o campo {keys[0]}"
    else:
        campos = ", ".join(keys)
        frase = f"os campos {campos}"

    result_his = await api.register_historic_from_model(
        historic_model, f"atualizou {frase} do usuario {user_data.get('alias', '')} !"
    )

    if result_his.is_failure:
        response = Response(code=500, log=result_his.value, details=result_his.details)
        return response.json()

    if result.is_failure:
        response = Response(code=500, log=result.value, details=result.details)
        return response.json()

    response = Response(code=200, data=result.value, log=result.log)
    return response.json()


# -------------------------------
# Rota para abrir porta (reconhecimento facial)
# -------------------------------
@app.post("/open_door")
async def open_door(request: Request):
    form = await request.json()
    device_data = form.get("device", {})
    device_model = DeviceModel(**device_data)

    # Comando assíncrono para abrir porta
    command = AsyncCommand(lambda: api_repository.open_door(device_model))
    result = await command.execute_async()

    if result.is_failure:
        status_code = 500 if result.error else 403
        response = Response(
            data=result.to_map(),
            code=status_code,
            log=result.log,
        )
        return response.json()

    # Cria histórico da ação de abertura da porta
    historic_dict = dict(result.value) | device_model.model_dump_all()
    historic_model = HistoricModel(**historic_dict)
    result_his = await api.register_historic_from_model(
        historic_model, f" entrou em {device_model.local} !"
    )

    if result_his.is_failure:
        response = Response(code=500, log=result_his.value, details=result_his.details)
        return response.json()

    # Sucesso: porta aberta
    response = Response(
        data=result.to_map(),
        code=200,
        log=result.log,
    )
    return response.json()
