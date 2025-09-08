from copy import deepcopy
from datetime import datetime, timezone
from enum import StrEnum
from google.api_core.exceptions import NotFound as GoogleNotFound
from google.cloud import secretmanager
from google.oauth2.service_account import Credentials
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, Generic, Literal, Optional, TypeVar, Union, overload
from uuid import uuid4
from maleo.dtos.authentication import GenericAuthentication
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.data import DataPair
from maleo.dtos.resource import ResourceIdentifier
from maleo.enums.operation import (
    OperationType,
    ResourceOperationType,
    ResourceOperationCreateType,
)
from maleo.exceptions import NotFound, InternalServerError
from maleo.logging.config import Config
from maleo.logging.enums import Level
from maleo.mixins.timestamp import OperationTimestamp
from maleo.schemas.operation.resource import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    CreateSingleResourceOperation,
    ReadSingleResourceOperation,
)
from maleo.schemas.response import (
    SingleDataResponse,
    CreateSingleDataResponse,
    ReadSingleDataResponse,
)
from maleo.types.base.uuid import OptionalUUID
from .base import RESOURCE as BASE_RESOURCE, GoogleClientManager


RESOURCE = deepcopy(BASE_RESOURCE)
RESOURCE.identifiers.append(
    ResourceIdentifier(key="secret", name="Secret", slug="secret")
)


class Format(StrEnum):
    BYTES = "bytes"
    STRING = "string"


FORMAT_TYPE_MAPPING: Dict[Format, type] = {
    Format.BYTES: bytes,
    Format.STRING: str,
}


ValueT = TypeVar("ValueT", bytes, str)


class Secret(BaseModel, Generic[ValueT]):
    name: str = Field(..., description="Secret's name")
    version: str = Field("latest", description="Secret's version")
    value: ValueT = Field(..., description="Secret's value")


class GoogleSecretManager(GoogleClientManager):
    def __init__(
        self,
        log_config: Config,
        *,
        service_context: Optional[ServiceContext] = None,
        credentials: Optional[Credentials] = None,
        credentials_path: Optional[Union[Path, str]] = None,
    ) -> None:
        super().__init__(
            "google-secret-manager",
            "GoogleSecretManager",
            log_config,
            service_context,
            credentials,
            credentials_path,
        )
        self._client = secretmanager.SecretManagerServiceClient(
            credentials=self._credentials
        )

    def create(
        self,
        name: str,
        value: ValueT,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> SingleDataResponse[Secret[ValueT], None]:
        if not isinstance(value, (bytes, str)):
            raise TypeError("Value type can only either be 'bytes' or 'str'")

        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = CreateResourceOperationAction(
            type=ResourceOperationType.CREATE,
            create_type=ResourceOperationCreateType.NEW,
        )

        resource = deepcopy(RESOURCE)
        resource.details = {"name": name}

        executed_at = datetime.now(tz=timezone.utc)

        parent = f"projects/{self._credentials.project_id}"
        secret_path = f"{parent}/secrets/{name}"
        # Check if the secret already exists
        try:
            request = secretmanager.GetSecretRequest(name=secret_path)
            self._client.get_secret(request=request)
        except GoogleNotFound:
            # Secret does not exist, create it first
            try:
                secret = secretmanager.Secret(name=name, replication={"automatic": {}})
                request = secretmanager.CreateSecretRequest(
                    parent=parent, secret_id=name, secret=secret
                )
                self._client.create_secret(request=request)
            except Exception as e:
                raise InternalServerError[Optional[GenericAuthentication]](
                    OperationType.RESOURCE,
                    service_context=self._service_context,
                    operation_id=operation_id,
                    operation_context=self._operation_context,
                    operation_timestamp=OperationTimestamp.completed_now(executed_at),
                    operation_summary="Unexpected error raised while creating new secret",
                    request_context=request_context,
                    authentication=authentication,
                    operation_action=operation_action,
                    resource=RESOURCE,
                    details={
                        "exc_type": type(e).__name__,
                        "exc_data": {
                            "message": str(e),
                            "args": e.args,
                        },
                    },
                ) from e

        # Add a new secret version
        try:
            bytes_value = value.encode() if isinstance(value, str) else value
            payload = secretmanager.SecretPayload(data=bytes_value)
            request = secretmanager.AddSecretVersionRequest(
                parent=secret_path, payload=payload
            )
            self._client.add_secret_version(request=request)
            completed_at = datetime.now(tz=timezone.utc)

            secret = Secret[ValueT](name=name, version="latest", value=value)
            operation_response_data = DataPair[None, Secret[ValueT]](
                old=None,
                new=secret,
            )
            operation_response = CreateSingleDataResponse[Secret[ValueT], None](
                data=operation_response_data, metadata=None, other=None
            )
            CreateSingleResourceOperation[
                Optional[GenericAuthentication], Secret[ValueT], None
            ](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary=f"Successfully added new secret '{name}' version",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                resource=RESOURCE,
                response=operation_response,
            ).log(
                self._logger, Level.INFO
            )

            return SingleDataResponse[Secret[ValueT], None](
                data=secret,
                metadata=None,
                other=None,
            )

        except Exception as e:
            raise InternalServerError[Optional[GenericAuthentication]](
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="Unexpected error raised while adding new secret version",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=RESOURCE,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            ) from e

    @overload
    def read(
        self,
        format: Literal[Format.BYTES],
        name: str,
        version: str = "latest",
        *,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> SingleDataResponse[Secret[bytes], None]: ...
    @overload
    def read(
        self,
        format: Literal[Format.STRING],
        name: str,
        version: str = "latest",
        *,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> SingleDataResponse[Secret[str], None]: ...
    def read(
        self,
        format: Format,
        name: str,
        version: str = "latest",
        *,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> Union[
        SingleDataResponse[Secret[bytes], None],
        SingleDataResponse[Secret[str], None],
    ]:
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = ReadResourceOperationAction()

        resource = deepcopy(RESOURCE)
        resource.details = {"name": name, "version": version}

        value_type = FORMAT_TYPE_MAPPING.get(format, None)
        if value_type is None:
            raise ValueError(
                f"Unable to determine secret value type for given format: '{format}'"
            )

        executed_at = datetime.now(tz=timezone.utc)

        # Check if secret exists
        secret_name = f"projects/{self._credentials.project_id}/secrets/{name}"
        try:
            request = secretmanager.GetSecretRequest(name=secret_name)
            self._client.get_secret(request=request)
        except GoogleNotFound as gnf:
            raise NotFound[Optional[GenericAuthentication]](
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary=f"Secret '{secret_name}' not found",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=RESOURCE,
                details=gnf.reason,
            ) from gnf
        except Exception as e:
            raise InternalServerError[Optional[GenericAuthentication]](
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary=f"Exception raised while ensuring secret '{secret_name}' exists",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=RESOURCE,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            ) from e

        # Check if secret's version exists
        secret_version_name = f"{secret_name}/versions/{version}"
        try:
            request = secretmanager.GetSecretVersionRequest(name=secret_version_name)
            self._client.get_secret_version(request=request)
        except GoogleNotFound as gnf:
            raise NotFound[Optional[GenericAuthentication]](
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary=f"Secret's version '{secret_version_name}' not found",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=RESOURCE,
                details=gnf.reason,
            ) from gnf
        except Exception as e:
            raise InternalServerError(
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary=f"Exception raised while ensuring secret's version '{secret_version_name}' exists",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=RESOURCE,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            ) from e

        try:
            request = secretmanager.AccessSecretVersionRequest(name=secret_version_name)
            response = self._client.access_secret_version(request=request)
            completed_at = datetime.now(tz=timezone.utc)

            if format is Format.BYTES:
                value = response.payload.data
            elif format is Format.STRING:
                value = response.payload.data.decode()

            secret = Secret[value_type](name=name, version=version, value=value)
            operation_response_data = DataPair[Secret[value_type], None](
                old=secret, new=None
            )
            operation_response = ReadSingleDataResponse[Secret[value_type], None](
                data=operation_response_data, metadata=None, other=None
            )

            ReadSingleResourceOperation[
                Optional[GenericAuthentication], Secret[value_type], None
            ](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary=f"Successfully retrieved secret '{name}' with version '{version}'",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                resource=RESOURCE,
                response=operation_response,
            ).log(
                self._logger, Level.INFO
            )

            return SingleDataResponse[Secret[value_type], None](
                data=secret,
                metadata=None,
                other=None,
            )

        except Exception as e:
            raise InternalServerError[Optional[GenericAuthentication]](
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary=f"Exception raised while accessing secret's version '{secret_version_name}'",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=RESOURCE,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            ) from e
