import asyncio
from datetime import date, datetime

from controllers.api_controller import ApiController
from core.commands.async_command import AsyncCommand
from core.commands.stream_command import StreamCommand
from core.config.app_config import CameraConfig, DatabaseTables
from core.utils.api_utils import ApiUtils
from models.device_model import DeviceModel
from models.face_model import FaceModel
from models.historic_model import HistoricModel
from models.login_model import LoginModel
from models.user_model import UserModel

from repository.api_repository import ApiRepository
from repository.camera_repository import CameraRepository
from repository.database_repository import DatabaseRepository

from repository.face_repository import FaceRepository
from services.face_service import FaceService


face_model = FaceModel()

cam_repository = CameraRepository(CameraConfig())
face_service = FaceService(cam_repository)

db_repository = DatabaseRepository()
face_repository = FaceRepository(face_service, face_model)

api_repository = ApiRepository(db_repository, face_repository)


async def debug_async():
    user_admin_dict = {"email": "root.debug@gmail.com", "senha": "@Isac1998"}
    user_admin = LoginModel(**user_admin_dict)

    controller = ApiController(api_repository, face_service)

    user_discente_dict = {
        "nome": "João Silva",
        "alias": "joaos",
        "cpf": "123.456.789-00",
        "email": "joao.silva@email.com",
        "matricula": "2025123456",
        "senha": None,
        "icon_path": None,
        "encodings": None,
    }

    user_discente = UserModel(**user_discente_dict)

    stream_command = StreamCommand(
        lambda: controller.register_user_db(user_discente, user_admin)
    )

    async for result in stream_command.execute_stream():
        print(result)


async def teste_async():
    historic_dict = {
        "nome": "root",
        "alias": "root",
        "id": "00000001",
        "email": "root.debug@gmail.com",
        "matricula": "123456",
    }

    historic_model = HistoricModel(**historic_dict)

    historic_model.set_log("teste login")

    controller = ApiController(api_repository, face_service)

    result = await controller.register_historic(historic_model)

    print(result)
    


def debug():
    print(ApiUtils._hash_sha256("admin123"))


if __name__ == "__main__":
    debug()
