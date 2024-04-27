"""
参数注入模板
"""
from __future__ import annotations

from abc import abstractmethod, ABC
from inspect import Parameter
from typing import Any


class Resolver(ABC):
    @abstractmethod
    def support_parameter(self, parameter: Parameter) -> bool:
        pass

    @abstractmethod
    async def support(self, parameter: Parameter, scope: dict) -> bool:
        pass

    @abstractmethod
    async def resolve(self, parameter: Parameter, scope: dict) -> Any:
        pass

    async def close(self, parameter, scope: dict, exc: Exception):
        pass


class Dependency(ABC):

    @abstractmethod
    async def support(self, parameter: Parameter, scope: dict) -> bool:
        pass

    @abstractmethod
    async def resolve(self, parameter: Parameter, scope: dict) -> Any:
        pass

    async def close(self, parameter: Parameter, scope: dict, exc: Exception):
        pass
