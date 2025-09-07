import logging
import os
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional, Union, overload
from maleo.enums.environment import Environment
from maleo.enums.service import Key
from maleo.types.base.dict import StringToStringDict
from maleo.types.base.string import OptionalString
from .config import Config
from .enums import LoggerType


# * We suggest to NOT use this class
# * Instead use the inherited classes
class Base(logging.Logger):
    def __init__(
        self,
        type: LoggerType = LoggerType.BASE,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        client_key: OptionalString = None,
        config: Config,
    ):
        self._type = type  # Declare logger type

        # Ensure environment exists
        actual_environment = environment or os.getenv("ENVIRONMENT")
        if actual_environment is None:
            raise ValueError(
                "ENVIRONMENT environment variable must be set if 'environment' is set to None"
            )
        else:
            self._environment = Environment(actual_environment)

        # Ensure service_key exists
        actual_service_key = service_key or os.getenv("SERVICE_KEY")
        if actual_service_key is None:
            raise ValueError(
                "SERVICE_KEY environment variable must be set if 'service_key' is set to None"
            )
        else:
            self._service_key = Key(actual_service_key)

        self._client_key = client_key  # Declare client key

        # Ensure client_key is valid if logger type is a client
        if self._type == LoggerType.CLIENT and self._client_key is None:
            raise ValueError(
                "'client_key' parameter must be provided if 'logger_type' is 'client'"
            )

        # Define logger name
        base_name = f"{self._environment} - {self._service_key} - {self._type}"
        if self._type == LoggerType.CLIENT:
            self._name = f"{base_name} - {self._client_key}"
        else:
            self._name = base_name

        # Define log labels
        self._labels: StringToStringDict = {
            "logger_type": self._type.value,
            "service_environment": self._environment.value,
            "service_key": self._service_key.value,
        }
        if client_key is not None:
            self._labels["client_key"] = client_key
        if config.labels is not None:
            self._labels.update(config.labels)

        self._config = config

        super().__init__(self._name, self._config.level)  # Init the superclass's logger

        # Clear existing handlers to prevent duplicates
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.addHandler(console_handler)

        # Google Cloud Logging handler (If enabled)
        if self._config.google_cloud_logging is not None:
            cloud_logging_handler = self._config.google_cloud_logging.create_handler(
                name=self._name.replace(" ", ""),
                labels=self._labels,
            )
            self.addHandler(cloud_logging_handler)
        else:
            self.warning(
                "Cloud logging is not configured. Will not add cloud logging handler"
            )

        # Define aggregate log directory
        if self._config.aggregate_file_name is not None:
            aggregate_log_dir = os.path.join(self._log_dir, "aggregate")
            os.makedirs(aggregate_log_dir, exist_ok=True)
            if not self._config.aggregate_file_name.endswith(".log"):
                self._config.aggregate_file_name += ".log"
            log_filename = os.path.join(
                aggregate_log_dir, self._config.aggregate_file_name
            )

            # File handler
            file_handler = logging.FileHandler(log_filename, mode="a")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.addHandler(file_handler)

        # Define individual log directory
        if self._config.individual_log:
            if self._type == LoggerType.CLIENT:
                log_dir = f"{self._type}/{self._client_key}"
            else:
                log_dir = f"{self._type}"
            self._log_dir = os.path.join(self._config.dir, log_dir)
            os.makedirs(self._log_dir, exist_ok=True)

            # Generate timestamped filename
            log_filename = os.path.join(
                self._log_dir,
                f"{datetime.now(tz=timezone.utc).isoformat(timespec="seconds")}.log",
            )

            # File handler
            file_handler = logging.FileHandler(log_filename, mode="a")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.addHandler(file_handler)

    def dispose(self):
        """Dispose of the logger by removing all handlers."""
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()
        self.handlers.clear()


class Application(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ):
        super().__init__(
            LoggerType.APPLICATION,
            environment=environment,
            service_key=service_key,
            client_key=None,
            config=config,
        )


class Cache(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ):
        super().__init__(
            LoggerType.CACHE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            config=config,
        )


class Client(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        client_key: str,
        config: Config,
    ):
        super().__init__(
            LoggerType.CACHE,
            environment=environment,
            service_key=service_key,
            client_key=client_key,
            config=config,
        )


class Controller(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ):
        super().__init__(
            LoggerType.CONTROLLER,
            environment=environment,
            service_key=service_key,
            client_key=None,
            config=config,
        )


class Database(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ):
        super().__init__(
            LoggerType.DATABASE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            config=config,
        )


class Exception(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ):
        super().__init__(
            LoggerType.EXCEPTION,
            environment=environment,
            service_key=service_key,
            client_key=None,
            config=config,
        )


class Middleware(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ):
        super().__init__(
            LoggerType.MIDDLEWARE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            config=config,
        )


class Repository(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ):
        super().__init__(
            LoggerType.REPOSITORY,
            environment=environment,
            service_key=service_key,
            client_key=None,
            config=config,
        )


class Service(Base):
    def __init__(
        self,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ):
        super().__init__(
            LoggerType.SERVICE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            config=config,
        )


@overload
def create(
    type: Literal[LoggerType.APPLICATION],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    config: Config,
) -> Application: ...
@overload
def create(
    type: Literal[LoggerType.CACHE],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    config: Config,
) -> Cache: ...
@overload
def create(
    type: Literal[LoggerType.CLIENT],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    client_key: str,
    config: Config,
) -> Client: ...
@overload
def create(
    type: Literal[LoggerType.CONTROLLER],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    config: Config,
) -> Controller: ...
@overload
def create(
    type: Literal[LoggerType.DATABASE],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    config: Config,
) -> Database: ...
@overload
def create(
    type: Literal[LoggerType.EXCEPTION],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    config: Config,
) -> Exception: ...
@overload
def create(
    type: Literal[LoggerType.MIDDLEWARE],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    config: Config,
) -> Middleware: ...
@overload
def create(
    type: Literal[LoggerType.REPOSITORY],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    config: Config,
) -> Repository: ...
@overload
def create(
    type: Literal[LoggerType.SERVICE],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    config: Config,
) -> Service: ...
def create(
    type: LoggerType = LoggerType.BASE,
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    client_key: OptionalString = None,
    config: Config,
) -> Union[
    Base,
    Application,
    Cache,
    Client,
    Controller,
    Database,
    Exception,
    Middleware,
    Repository,
    Service,
]:
    if type is LoggerType.BASE:
        return Base(
            environment=environment,
            service_key=service_key,
            client_key=client_key,
            config=config,
        )
    elif type is LoggerType.APPLICATION:
        return Application(
            environment=environment,
            service_key=service_key,
            config=config,
        )
    elif type is LoggerType.CACHE:
        return Cache(
            environment=environment,
            service_key=service_key,
            config=config,
        )
    elif type is LoggerType.CLIENT:
        if client_key is None:
            raise ValueError(
                "Argument 'client_key' can not be None if 'logger_type' is 'client'"
            )
        return Client(
            environment=environment,
            service_key=service_key,
            client_key=client_key,
            config=config,
        )
    elif type is LoggerType.CONTROLLER:
        return Controller(
            environment=environment,
            service_key=service_key,
            config=config,
        )
    elif type is LoggerType.DATABASE:
        return Database(
            environment=environment,
            service_key=service_key,
            config=config,
        )
    elif type is LoggerType.EXCEPTION:
        return Exception(
            environment=environment,
            service_key=service_key,
            config=config,
        )
    elif type is LoggerType.MIDDLEWARE:
        return Middleware(
            environment=environment,
            service_key=service_key,
            config=config,
        )
    elif type is LoggerType.REPOSITORY:
        return Repository(
            environment=environment,
            service_key=service_key,
            config=config,
        )
    elif type is LoggerType.SERVICE:
        return Service(
            environment=environment,
            service_key=service_key,
            config=config,
        )


class Loggers(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    application: Application = Field(..., description="Application logger")
    cache: Cache = Field(..., description="Cache logger")
    controller: Controller = Field(..., description="Controller logger")
    database: Database = Field(..., description="Database logger")
    exception: Exception = Field(..., description="Exception logger")
    middleware: Middleware = Field(..., description="Middleware logger")
    repository: Repository = Field(..., description="Repository logger")
    service: Service = Field(..., description="Service logger")

    @classmethod
    def create(
        cls,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        config: Config,
    ) -> "Loggers":
        return cls(
            application=create(
                LoggerType.APPLICATION,
                environment=environment,
                service_key=service_key,
                config=config,
            ),
            cache=create(
                LoggerType.CACHE,
                environment=environment,
                service_key=service_key,
                config=config,
            ),
            controller=create(
                LoggerType.CONTROLLER,
                environment=environment,
                service_key=service_key,
                config=config,
            ),
            database=create(
                LoggerType.DATABASE,
                environment=environment,
                service_key=service_key,
                config=config,
            ),
            exception=create(
                LoggerType.EXCEPTION,
                environment=environment,
                service_key=service_key,
                config=config,
            ),
            middleware=create(
                LoggerType.MIDDLEWARE,
                environment=environment,
                service_key=service_key,
                config=config,
            ),
            repository=create(
                LoggerType.REPOSITORY,
                environment=environment,
                service_key=service_key,
                config=config,
            ),
            service=create(
                LoggerType.SERVICE,
                environment=environment,
                service_key=service_key,
                config=config,
            ),
        )
