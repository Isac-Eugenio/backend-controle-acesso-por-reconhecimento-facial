from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi import FastAPI

import asyncio
import json

from fastapi.responses import JSONResponse, StreamingResponse

from controllers.api_controller import ApiController
from core.commands.async_command import AsyncCommand
from core.commands.stream_command import StreamCommand
from core.config.app_config import CameraConfig
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

camera_repository = CameraRepository(CameraConfig())

db_repository = DatabaseRepository()

face_service = FaceService(camera_repository)

face_model = FaceModel()

face_repository = FaceRepository(face_service, face_model)

api_repository = ApiRepository(db_repository, face_repository)

api = ApiController(api_repository, face_service)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
async def login(request: Request):
    form = await request.json()

    result = await api.login(form)

    if result.is_success:

        data_dict = result.value.model_dump()

        response = Response(
            log="Login realizado com sucesso ...",
            data=data_dict,
            code=200,
        )

        historic_model = HistoricModel(**data_dict)

        result_his = await api.register_historic_from_model(
            historic_model, "logou no sistema !"
        )

        print(result_his)

        if result_his.is_failure:
            response = Response(
                log="Erro ao realizar login ..",
                details=result_his.details,
                error=result_his.value,
                code=500,
            )
            return response.json()

        return response.json()

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


@app.post("/logout")
async def logout(request: Request):
    form = await request.json()

    perfil = PerfilModel(**form)

    perfil_dict = perfil.model_dump()

    historic_model = HistoricModel(**perfil_dict)

    historic_model.set_log(f"Usuario {perfil.alias} deslogou no sistema !")

    result_his = await api.register_historic_from_model(
        historic_model, "deslogou no sistema !"
    )

    if result_his.is_failure:
        response = Response(
            log="Erro ao registrar logout..",
            details=result_his.details,
            error=result_his.value,
            code=500,
        )
        return response.json()

    response = Response(
        log="logout bem sucedido ...",
        details=result_his.details,
        code=200,
    )
    return response.json()


@app.post("/perfis")
async def table_perfil(request: Request):
    form = await request.json()

    model = LoginModel(**form)

    auth = await api.isAdmin(model)

    print(auth)

    if auth.value:
        result = await api.get_user_table()
        user_login = await api.login(form)

        if result.is_failure:
            response = Response(code=500, log=result.value, details=result.details)
            return response.json()

        perfil_auth_dict = user_login.value.model_dump()

        historic_model = HistoricModel(**perfil_auth_dict)

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

    if auth.is_failure:
        response = Response(code=403, log=auth.log, details=auth.details)
        return response.json()

    response = Response(code=401, log="Acesso Negado ...", details=auth.log)
    return response.json()


@app.post("/register_user")
async def register_user(request: Request):

    form = await request.json()

    user_data = form.get("user", {})
    admin_access = form.get("admin", {})

    user_model = UserModel(**user_data)
    login_model = LoginModel(**admin_access)

    command = StreamCommand(lambda: api.register_user_db(user_model, login_model))

    stream = StreamResponse(command)

    return await stream.response()


@app.post("/find_user")
async def find_user(request: Request):
    form = await request.json()

    user_data = form.get("user", {})

    admin_data = form.get("admin", {})

    command = AsyncCommand(lambda: api.find_user(user_data, admin_data))

    result = await command.execute_async()

    if result.is_failure:
        response = Response(code=500, log=result.value, details=result.details)
        return response.json()

    historic_model = HistoricModel(**admin_data)

    result_his = await api.register_historic_from_model(
        historic_model, f"consultou dados do usuario {result.value.alias} !"
    )

    if result_his.is_failure:
        response = Response(code=500, log=result_his.value, details=result_his.details)
        return response.json()

    response = Response(code=200, data=result.value, log=result.log)
    return response.json()


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
    
    historic_model = HistoricModel(**admin_data)

    result_his = await api.register_historic_from_model(
        historic_model, f"deletou o usuario {user_data.get('alias', '')} !"
    )
    
    if result_his.is_failure:
        response = Response(code=500, log=result_his.value, details=result_his.details)
        return response.json()

    response = Response(code=200, data=result.value, log=result.log)
    return response.json()


@app.post("/update_user")
async def update_user(request: Request):
    form = await request.json()

    user_data = form.get("user", {})
    admin_data = form.get("admin", {})
    new_data = form.get("new_data", {})
    
    command = AsyncCommand(lambda: api.update_user(user_data, new_data, admin_data))

    result = await command.execute_async()

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


@app.post("/open_door")
async def open_door(request: Request):
    form = await request.json()

    device_data = form.get("device", {})
    device_model = DeviceModel(**device_data)

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
    
    historic_dict = dict(result.value) | device_model.model_dump_all()

    historic_model = HistoricModel(**historic_dict)

    result_his = await api.register_historic_from_model(
        historic_model, f" entrou em {device_model.local} !"
    )

    if result_his.is_failure:
        response = Response(code=500, log=result_his.value, details=result_his.details)
        return response.json()

    # caso de sucesso
    response = Response(
        data=result.to_map(),
        code=200,
        log=result.log,
    )
    return response.json()
