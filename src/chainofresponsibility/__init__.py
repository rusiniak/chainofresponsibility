from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Self


@dataclass
class Application:
    id: str
    name: str
    yearly_income: int
    employment_score: int
    history_score: int
    is_employed: bool
    offers: List[str] = field(default_factory=list)


def are_offers_available(application: Application) -> bool:
    return bool(application.offers)


class InterfaceHandler(ABC):
    def __init__(
        self,
        handling_criteria_function: Callable[
            [Application], bool
        ] = lambda application: True,
    ):
        self._next_handler: Optional[Self] = None
        self.handling_criteria_function = handling_criteria_function

    @property
    def next_handler(self):
        return self._next_handler

    @next_handler.setter
    def next_handler(self, next_handler: Self) -> Self:
        self._next_handler = next_handler

    def handle_application(self, application: Application):
        if self.handling_criteria_function(application):
            application = self._process_application(application)
        if self.next_handler:
            return self.next_handler.handle_application(application)
        return application

    @abstractmethod
    def _process_application(self, application: Application) -> Application:
        ...


class EmploymentHandler(InterfaceHandler):
    def _process_application(self, application: Application) -> Application:
        if application.is_employed and application.employment_score > 0:
            application.offers.append(f"{self.__class__.__name__} offer")
        else:
            application.offers.clear()
        print(f"{self.__class__.__name__} processed application")
        return application


class IncomeHandler(EmploymentHandler):
    def _process_application(self, application: Application) -> Application:
        if application.yearly_income > 1000:
            application.offers.append(f"{self.__class__.__name__} offer")
        else:
            application.offers.clear()
        print(f"{self.__class__.__name__} processed application")
        return application


class HistoryHandler(EmploymentHandler):
    def _process_application(self, application: Application) -> Application:
        if application.history_score > 0:
            application.offers.append(f"{self.__class__.__name__} offer")
        else:
            application.offers.clear()
        print(f"{self.__class__.__name__} processed application")
        return application


@dataclass
class HandlerConfig:
    handler_type: type(InterfaceHandler)
    handling_criteria_function: Optional[Callable[[Application], bool]] = None


class ChainConfig(list):
    def __init__(self, iterable=None):
        """Override initializer which can accept iterable"""
        super().__init__()
        if iterable:
            for item in iterable:
                self.append(item)

    def append(self, item):
        if isinstance(item, HandlerConfig):
            super().append(item)
        else:
            raise ValueError("HandlerConfig allowed only")

    def insert(self, index, item):
        if isinstance(item, HandlerConfig):
            super().insert(index, item)
        else:
            raise ValueError("HandlerConfig allowed only")

    def __add__(self, item):
        if isinstance(item, HandlerConfig):
            super().__add__(item)
        else:
            raise ValueError("HandlerConfig allowed only")

    def __iadd__(self, item):
        if isinstance(item, HandlerConfig):
            super().__iadd__(item)
        else:
            raise ValueError("HandlerConfig allowed only")


@dataclass
class ChainFactory:
    chain_config: ChainConfig

    def build_chain(self) -> InterfaceHandler:
        handlers = []
        for handler_config in self.chain_config:
            kwargs = {}
            if handler_config.handling_criteria_function:
                kwargs[
                    "handling_criteria_function"
                ] = handler_config.handling_criteria_function
            handlers.append(handler_config.handler_type(**kwargs))
        return self._setup_chain(handlers)

    @staticmethod
    def _setup_chain(handlers: List[InterfaceHandler]):
        handlers_iterator = iter(handlers)
        first_handler = previous_handler = next(handlers_iterator)
        for handler in handlers:
            previous_handler.next_handler = handler
            previous_handler = handler
        return first_handler


def create_chain_of_responsibility(
    chain_configuration: ChainConfig,
) -> InterfaceHandler:
    factory = ChainFactory(chain_configuration)
    return factory.build_chain()
