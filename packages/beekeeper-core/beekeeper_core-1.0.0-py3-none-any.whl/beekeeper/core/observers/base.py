from abc import ABC, abstractmethod
from typing import Optional

from beekeeper.core.observers.types import PayloadRecord
from beekeeper.core.prompts import PromptTemplate


class BaseObserver(ABC):
    """An interface for observability."""

    @classmethod
    def class_name(cls) -> str:
        return "BaseObserver"


class ModelObserver(BaseObserver):
    """An interface for model observability."""

    def __init__(self, prompt_template: Optional[PromptTemplate] = None) -> None:
        self.prompt_template = prompt_template

    @classmethod
    def class_name(cls) -> str:
        return "ModelObserver"

    @abstractmethod
    def __call__(self, payload: PayloadRecord) -> None:
        """ModelObserver."""


class TelemetryObserver(BaseObserver):
    """An interface for telemetry observability."""

    @classmethod
    def class_name(cls) -> str:
        return "TelemetryObserver"
