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
    """
    Repositório para interação com o banco de dados MySQL de forma assíncrona.
    Permite executar queries de SELECT, INSERT, UPDATE, DELETE e contagem.
    Usa DatabaseCommand como wrapper para execução das queries.
    """

    def __init__(self, database_url=None):
        """Inicializa a conexão e o comando de banco"""
        self.database_url = database_url or DATABASE_URL
        self.database = AsyncDatabase(self.database_url)
        self.isconnected: Result = Failure(
            "Banco ainda não conectado", log="Conexão não inicializada"
        )
        self.command = DatabaseCommand(self.database)

    async def select_one(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        """Executa SELECT retornando apenas um registro"""
        query.select()
        result = await self.command.execute_query(query=query, type_fetch="one")
        if result.is_success:
            return Success(result.value, log="Select one executado com sucesso")
        else:
            return Failure(
                result.value,
                log="Erro ao executar Select one",
                details=str(result.details),
            )

    async def select(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        """Executa SELECT retornando todos os registros"""
        query.select()
        result = await self.command.execute_query(query=query, type_fetch="all")
        if result.is_success:
            return Success(result.value, log="Select All executado com sucesso")
        else:
            return Failure(
                result.value,
                log="Erro ao executar Select All",
                details=str(result.details),
            )

    async def insert(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        """Executa INSERT usando os valores do query"""
        query.insert()
        result = await self.command.execute_query(query=query)
        if result.is_success:
            return Success(result.value, log="Insert executado com sucesso")
        else:
            return Failure(
                result.value, log="Erro ao executar Insert", details=str(result.details)
            )

    async def delete(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        """Executa DELETE usando os valores do query"""
        query.delete()
        result = await self.command.execute_query(query=query)
        if result.is_success:
            return Success(result.value, log="Delete executado com sucesso")
        else:
            return Failure(
                result.value, log="Erro ao executar Delete", details=str(result.details)
            )

    async def update(
        self, query: QueryModel, new_query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        """Executa UPDATE com cláusula SET de new_query e WHERE de query"""
        query.update(new_query)
        result = await self.command.execute_query(query=query)
        if result.is_success:
            return Success(result.value, log="Update executado com sucesso")
        else:
            return Failure(
                result.value, log="Erro ao executar Update", details=str(result.details)
            )

    async def count(
        self, query: QueryModel
    ) -> Result[Union[record, List[record], int], str]:
        """Executa SELECT COUNT(*) usando os filtros do query"""
        query.count()
        result = await self.command.execute_query(query=query, type_fetch="one")
        if result.is_success:
            return Success(result.value, log="Count executado com sucesso")
        else:
            return Failure(
                result.value, log="Erro ao executar Count", details=str(result.details)
            )
