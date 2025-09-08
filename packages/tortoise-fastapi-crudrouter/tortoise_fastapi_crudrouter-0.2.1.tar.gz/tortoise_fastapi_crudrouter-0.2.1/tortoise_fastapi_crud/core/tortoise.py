from typing import Any, List, Optional, Callable, Coroutine, cast
from fastapi import APIRouter, HTTPException, Depends
from tortoise.models import Model

from ._types import PAGINATION, RouteConfig, SchemaConfig
from ._utils import pagination_factory

NOT_FOUND = HTTPException(404, "Item not found")

CALLABLE = Callable[..., Coroutine[Any, Any, Model]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, List[Model]]]


class TortoiseCRUDRouter(APIRouter):
    def __init__(
        self,
        schema_config: SchemaConfig,
        route_config: Optional[RouteConfig] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(prefix=schema_config.prefix or "",
                         tags=schema_config.tags or [], **kwargs)

        self.schema_config = schema_config
        self.route_config = route_config or RouteConfig()

        self.db_model = self.schema_config.db_model
        self.schema = self.schema_config.schema or self.schema_config.create_schema or self.schema_config.update_schema
        self.create_schema = self.schema_config.create_schema or self.schema
        self.update_schema = self.schema_config.update_schema or self.schema
        self.paginate = self.schema_config.paginate

        self._register_routes()

    def _get_all(self) -> CALLABLE_LIST:
        if self.paginate:
            async def route(
                pagination: PAGINATION = pagination_factory(
                    self.paginate if isinstance(self.paginate, int) else None),
            ) -> List[Model]:
                skip, limit = pagination.get("skip"), pagination.get("limit")
                query = self.db_model.all().offset(cast(int, skip))
                if limit:
                    query = query.limit(limit)
                return await query
        else:
            async def route() -> List[Model]:
                return await self.db_model.all()

        return route

    def _get_one(self) -> CALLABLE:
        async def route(item_id: int) -> Model:
            model = await self.db_model.filter(id=item_id).first()
            if model:
                return model
            raise NOT_FOUND
        return route

    def _create(self) -> CALLABLE:
        async def route(model: self.create_schema) -> Model:
            db_model = self.db_model(**model.model_dump())
            await db_model.save()
            return db_model
        return route

    def _update(self) -> CALLABLE:
        async def route(item_id: int, model: self.update_schema) -> Model:
            await self.db_model.filter(id=item_id).update(**model.model_dump(exclude_unset=True))
            return await self.db_model.get(id=item_id)
        return route

    def _delete_all(self) -> CALLABLE_LIST:
        async def route() -> List[Model]:
            await self.db_model.all().delete()
            return []
        return route

    def _delete_one(self) -> CALLABLE:
        async def route(item_id: int) -> Model:
            model: Model = await self.db_model.filter(id=item_id).first()
            if not model:
                raise NOT_FOUND
            await self.db_model.filter(id=item_id).delete()
            return model
        return route

    def _register_routes(self) -> None:
        if self.route_config.get_all_route:
            self.add_api_route("/", self._get_all(),
                               response_model=List[self.schema], methods=["GET"])

        if self.route_config.get_one_route:
            self.add_api_route("/{item_id}", self._get_one(),
                               response_model=self.schema, methods=["GET"])

        if self.route_config.create_route:
            self.add_api_route("/", self._create(),
                               response_model=self.schema, methods=["POST"])

        if self.route_config.update_route:
            self.add_api_route("/{item_id}", self._update(),
                               response_model=self.schema, methods=["PUT"])

        if self.route_config.delete_all_route:
            self.add_api_route("/", self._delete_all(),
                               response_model=List[self.schema], methods=["DELETE"])

        if self.route_config.delete_one_route:
            self.add_api_route("/{item_id}", self._delete_one(),
                               response_model=self.schema, methods=["DELETE"])

    @staticmethod
    def get_routes() -> List[str]:
        return ["get_all", "create", "delete_all", "get_one", "update", "delete_one"]
