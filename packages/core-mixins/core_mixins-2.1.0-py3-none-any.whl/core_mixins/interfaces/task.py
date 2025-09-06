# -*- coding: utf-8 -*-

"""
This module provides a base implementation for ETL tasks
under the project ecosystem.
"""

from abc import ABC, abstractmethod
from enum import Enum
from logging import Logger
from typing import Any, Optional

from core_mixins.interfaces.factory import IFactory


class TaskStatus(str, Enum):
    """Possible status a task can have during its life"""

    CREATED = "CREATED"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class ITask(IFactory, ABC):
    """Base implementations for different tasks/processes"""

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        self._name = name
        self.description = description
        self._status = TaskStatus.CREATED
        self.logger = logger

    @classmethod
    def registration_key(cls) -> str:
        """It returns the key used to register the class"""
        return cls.__name__

    @property
    def name(self):
        """It returns the task identification"""
        return self._name or self.__class__.__name__

    @property
    def status(self) -> TaskStatus:
        """It returns the current status of the task"""
        return self._status

    @status.setter
    def status(self, status: TaskStatus) -> None:
        self._status = status

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """You must implement the task's process"""

        self.info(f"Executing: {self.name}")
        self.info(f"Purpose: {self.description}")

    def info(self, message) -> None:
        """Log entry with severity 'INFO'"""

        if self.logger:
            self.logger.info(f"{self.name} | {message}")

    def warning(self, message) -> None:
        """Log entry with severity 'WARNING'"""

        if self.logger:
            self.logger.warning(f"{self.name} | {message}")

    def error(self, error) -> None:
        """Log entry with severity 'ERROR'"""

        if self.logger:
            self.logger.error(f"{self.name} | {error}")


class TaskException(Exception):
    """Custom exception for Tasks"""
