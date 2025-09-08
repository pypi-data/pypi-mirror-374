from dataclasses import dataclass, field
from typing import Dict, List, Type, TypeVar, Optional, Sequence, Union
from xmlrpc.client import boolean

from fastapi.params import Depends
from pydantic import BaseModel, Field
from tortoise.models import Model

PAGINATION = Dict[str, Optional[int]]
PYDANTIC_SCHEMA = BaseModel

T = TypeVar("T", bound=BaseModel)
DEPENDENCIES = Optional[Sequence[Depends]]


@dataclass
class SchemaConfig:
    schema: Optional[Type[BaseModel]] = None
    db_model: Optional[Type[Model]] = None
    create_schema: Optional[PYDANTIC_SCHEMA] = None
    update_schema: Optional[PYDANTIC_SCHEMA] = None
    prefix: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    paginate: Optional[Union[int, bool]] = None


@dataclass
class RouteConfig:
    get_all_route: Union[bool, DEPENDENCIES] = True
    get_one_route: Union[bool, DEPENDENCIES] = True
    create_route: Union[bool, DEPENDENCIES] = True
    update_route: Union[bool, DEPENDENCIES] = True
    delete_one_route: Union[bool, DEPENDENCIES] = True
    delete_all_route: Union[bool, DEPENDENCIES] = True
