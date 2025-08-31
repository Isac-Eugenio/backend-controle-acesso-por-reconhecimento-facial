from dataclasses import dataclass
from typing import List, Any, Optional, Union


@dataclass
class QueryModel:
    """
    Modelo de consulta SQL genérico, usado para construir dinamicamente queries
    de SELECT, INSERT, UPDATE, DELETE e COUNT para bancos de dados.

    Este modelo abstrai a construção de queries parametrizadas, permitindo o uso
    de dicionários para valores e condições, garantindo compatibilidade com
    parâmetros bind (prevenção contra SQL Injection).

    Campos:
        - table: nome da tabela alvo da query.
        - columns: colunas para SELECT (lista ou string). Default é "*".
        - condition: condição customizada (string SQL) que será adicionada ao WHERE.
        - values: dicionário ou lista de valores para bind nos parâmetros da query.
        - query: string final da query gerada.

    Métodos:
        - select(values=None): constrói uma query SELECT com as colunas,
          condições e parâmetros bind. Prioriza valores em 'values' e mantém
          condição adicional se fornecida.
        - insert(): constrói uma query INSERT a partir de 'values', usando
          placeholders para bind.
        - delete(): constrói uma query DELETE baseada em 'values' como condição.
        - update(new_query): constrói uma query UPDATE baseada nos valores atuais
          para a cláusula WHERE e nos valores de 'new_query.values' para SET.
          Prefixa os novos valores com 'set_' para evitar colisão.
        - count(): constrói uma query SELECT COUNT(*) para contar registros
          com base em 'values' ou 'condition'.

    Observações:
        - Todos os métodos geram queries parametrizadas, substituindo valores por
          placeholders com ":" (ex: :key) para compatibilidade com ORMs ou drivers
          SQL que suportam bind.
        - Facilita a construção dinâmica de queries sem precisar concatenar strings
          manualmente.
    """

    table: str
    columns: Optional[List[str]] = None
    condition: Optional[str] = None
    values: Optional[Union[List[Any], dict]] = None
    query: Optional[str] = None

    def select(self, values: dict = None):
        """
        SELECT: Monta uma query SELECT parametrizada.
        - Se `values` informado → cria condições WHERE para cada key=value.
        - Se `columns` definido → seleciona essas colunas; senão, seleciona '*'.
        - Se `condition` definido → adiciona à cláusula WHERE.
        """

        if values is not None:
            self.values = values

        if self.columns is None:
            self.columns = "*"
        else:
            if isinstance(self.columns, str):
                self.columns = [self.columns]
            elif not isinstance(self.columns, (list, tuple)):
                raise Exception(f"`columns` inválido: {type(self.columns)}")
            self.columns = ", ".join(self.columns)

        self.query = f"SELECT {self.columns} FROM {self.table}"

        where_parts = []

        if self.values:
            conditions = [f"{key} = :{key}" for key in self.values.keys()]
            where_parts.extend(conditions)

        if self.condition:
            where_parts.append(self.condition)

        if where_parts:
            self.query += " WHERE " + " AND ".join(where_parts)

    def insert(self):
        """
        INSERT: Monta uma query INSERT parametrizada.
        - Usa `values` como dicionário de colunas e valores.
        """
        if not isinstance(self.values, dict):
            raise Exception("values não é um Map (Obrigatório)")
        columns = ", ".join(self.values.keys())
        placeholders = ", ".join([f":{key}" for key in self.values.keys()])
        self.query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"

    def delete(self):
        """
        DELETE: Monta uma query DELETE parametrizada.
        - Usa `values` como dicionário para condições WHERE.
        """
        if not self.values or not isinstance(self.values, dict):
            raise Exception(
                "Para deletar, forneça um dicionário de condições em 'values'."
            )
        conditions = [f"{key} = :{key}" for key in self.values.keys()]
        where_clause = " AND ".join(conditions)
        self.query = f"DELETE FROM {self.table} WHERE {where_clause}"

    def update(self, new_query: "QueryModel"):
        """
        UPDATE: Monta uma query UPDATE parametrizada.
        - `values` do modelo atual → condições WHERE.
        - `new_query.values` → dados para SET.
        """
        if not self.values or not isinstance(self.values, dict):
            raise Exception(
                "Forneça um dicionário de condições em 'values' para a cláusula WHERE."
            )
        if not new_query or not isinstance(new_query.values, dict):
            raise Exception(
                "Forneça um dicionário de dados a serem atualizados em 'new_query.values' para a cláusula SET."
            )

        set_clause = ", ".join(
            [f"{key} = :set_{key}" for key in new_query.values.keys()]
        )
        where_clause = " AND ".join([f"{key} = :{key}" for key in self.values.keys()])
        self.query = f"UPDATE {self.table} SET {set_clause} WHERE {where_clause}"

        new_values_prefixed = {f"set_{k}": v for k, v in new_query.values.items()}
        self.values = {**new_values_prefixed, **self.values}

    def count(self):
        """
        COUNT: Monta uma query SELECT COUNT(*).
        - Se `values` → cria condições WHERE para cada key=value.
        - Se `condition` → adiciona à cláusula WHERE.
        """
        self.query = f"SELECT COUNT(*) as total FROM {self.table}"
        where_parts = []

        if self.values:
            conditions = [f"{key} = :{key}" for key in self.values.keys()]
            where_parts.extend(conditions)
        elif self.condition:
            where_parts.append(self.condition)

        if where_parts:
            self.query += " WHERE " + " AND ".join(where_parts)
