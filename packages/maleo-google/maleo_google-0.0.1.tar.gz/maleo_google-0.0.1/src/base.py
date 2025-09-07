from google.oauth2.service_account import Credentials
from pathlib import Path
from typing import Optional, Union
from maleo.dtos.contexts.operation import generate_operation_context
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.resource import Resource, ResourceIdentifier
from maleo.enums.operation import Origin, Layer, Target
from maleo.logging.config import Config
from maleo.logging.logger import Client
from maleo.utils.loaders.credential.google import load


RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="google", name="Google", slug="google")],
    details=None,
)


class GoogleClientManager:
    def __init__(
        self,
        key: str,
        name: str,
        log_config: Config,
        service_context: Optional[ServiceContext] = None,
        credentials: Optional[Credentials] = None,
        credentials_path: Optional[Union[Path, str]] = None,
    ) -> None:
        self._key = key
        self._name = name

        self._logger = Client(
            environment=self._service_context.environment,
            service_key=self._service_context.key,
            client_key=self._key,
            config=log_config,
        )

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        if (credentials is None and credentials_path is None) or (
            credentials is not None and credentials_path is not None
        ):
            raise ValueError(
                "Only either 'credentials' and 'credentials_path' must be given"
            )

        if credentials is not None:
            self._credentials = credentials
        else:
            self._credentials = load(credentials_path)

        self._operation_context = generate_operation_context(
            origin=Origin.CLIENT, layer=Layer.SERVICE, target=Target.INTERNAL
        )
