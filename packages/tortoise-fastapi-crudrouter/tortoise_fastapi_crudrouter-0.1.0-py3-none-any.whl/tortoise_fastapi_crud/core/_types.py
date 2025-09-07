from typing import Dict, List, Type, TypeVar, Optional, Sequence, Union
from xmlrpc.client import boolean

from fastapi.params import Depends
from pydantic import BaseModel
from tortoise.models import Model

PAGINATION = Dict[str, Optional[int]]
PYDANTIC_SCHEMA = BaseModel

T = TypeVar("T", bound=BaseModel)
DEPENDENCIES = Optional[Sequence[Depends]]


class SchemaConfig(BaseModel):
    schema: Optional[Type[PYDANTIC_SCHEMA]] = None
    db_model: Optional[Type[Model]] = None
    create_schema: Optional[Type[PYDANTIC_SCHEMA]] = None
    update_schema: Optional[Type[PYDANTIC_SCHEMA]] = None
    prefix: Optional[str] = None
    tags: Optional[List[str]] = None
    paginate: Optional[Union[int, boolean]] = None


class RouteConfig(BaseModel):
    get_all_route: Union[bool, DEPENDENCIES] = True
    get_one_route: Union[bool, DEPENDENCIES] = True
    create_route: Union[bool, DEPENDENCIES] = True
    update_route: Union[bool, DEPENDENCIES] = True
    delete_one_route: Union[bool, DEPENDENCIES] = True
    delete_all_route: Union[bool, DEPENDENCIES] = True
