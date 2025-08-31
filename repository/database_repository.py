import asyncio
from typing import List, Union
from databases import Database as AsyncDatabase
from numpy import record

from core.commands.database_command import DatabaseCommand
from core.commands.result import Result, Success, Failure
from models.query_model import QueryModel
from core.config.app_config import DatabaseConfig as db

DATABASE_URL = f"mysql+aiomysql://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}"


class DatabaseRepository:
    def __init__(self, database_url=None):
        self.database_url = database_url or DATABASE_URL
        self.database = AsyncDatabase(self.database_url)
        self.isconnected: Result = Failure(
            "Banco ainda não conectado", log="Conexão não inicializada"
        )
        self.command = DatabaseCommand(self.database)

    async def select_one(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        query.select()
        result = await self.command.execute_query(query=query, type_fetch="one")
        if result.is_success:
            return Success(
                result.value, log="Select one executado com sucesso", details=""
            )
        else:
            return Failure(
                result.value,
                log="Erro ao executar Select one",
                details=str(result.details),
            )

    async def select(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        query.select()
        result = await self.command.execute_query(query=query, type_fetch="all")
        if result.is_success:
            return Success(
                result.value, log="Select All executado com sucesso", details=""
            )
        else:
            return Failure(
                result.value,
                log="Erro ao executar Select All",
                details=str(result.details),
            )

    async def insert(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        query.insert()
        result = await self.command.execute_query(query=query)
        if result.is_success:
            return Success(result.value, log="Insert executado com sucesso", details="")
        else:
            return Failure(
                result.value, log="Erro ao executar Insert", details=str(result.details)
            )

    async def delete(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        query.delete()
        result = await self.command.execute_query(query=query)
        if result.is_success:
            return Success(result.value, log="Delete executado com sucesso", details="")
        else:
            return Failure(
                result.value, log="Erro ao executar Delete", details=str(result.details)
            )

    async def update(
        self, query: QueryModel, new_query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        query.update(new_query)
        result = await self.command.execute_query(query=query)

        if result.is_success:
            return Success(result.value, log="Update executado com sucesso", details="")
        else:
            return Failure(
                result.value, log="Erro ao executar Update", details=str(result.details)
            )

    async def count(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        query.count()
        result = await self.command.execute_query(query=query, type_fetch="one")
        if result.is_success:
            return Success(result.value, log="Count executado com sucesso", details="")
        else:
            return Failure(
                result.value, log="Erro ao executar Count", details=str(result.details)
            )
