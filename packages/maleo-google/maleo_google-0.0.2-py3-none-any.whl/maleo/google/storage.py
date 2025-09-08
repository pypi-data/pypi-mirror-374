import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from google.cloud.storage import Bucket, Client
from google.oauth2.service_account import Credentials
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Union
from uuid import uuid4
from maleo.database.enums import Connection
from maleo.database.managers import RedisDatabaseManager
from maleo.dtos.authentication import GenericAuthentication
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.data import DataPair
from maleo.dtos.resource import AggregateField, ResourceIdentifier
from maleo.enums.cache import (
    Origin as CacheOrigin,
    Layer as CacheLayer,
)
from maleo.enums.expiration import Expiration
from maleo.enums.operation import (
    OperationType,
    ResourceOperationType,
    ResourceOperationCreateType,
    Target as OperationTarget,
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
from maleo.types.base.string import OptionalString
from maleo.types.base.uuid import OptionalUUID
from maleo.utils.cache import build_namespace, build_key
from .base import RESOURCE as BASE_RESOURCE, GoogleClientManager


RESOURCE = deepcopy(BASE_RESOURCE)
RESOURCE.identifiers.append(
    ResourceIdentifier(key="storage", name="Storage", slug="storage")
)


class Asset(BaseModel):
    url: str = Field(..., description="Asset's URL")


class GoogleCloudStorage(GoogleClientManager):
    def __init__(
        self,
        log_config: Config,
        *,
        service_context: Optional[ServiceContext] = None,
        credentials: Optional[Credentials] = None,
        credentials_path: Optional[Union[Path, str]] = None,
        bucket_name: OptionalString = None,
        redis: RedisDatabaseManager,
    ) -> None:
        super().__init__(
            "google-cloud-storage",
            "GoogleCloudStorage",
            log_config,
            service_context,
            credentials,
            credentials_path,
        )
        self._client = Client(credentials=self._credentials)

        self._bucket_name = None
        if bucket_name is not None:
            self._bucket_name = bucket_name
        else:
            env_bucket_name = os.getenv("GCS_BUCKET_NAME", None)
            if env_bucket_name is not None:
                self._bucket_name = env_bucket_name

        if self._bucket_name is None:
            self._client.close()
            raise ValueError(
                "Unable to determine 'bucket_name' either from argument or environment variable"
            )

        self._bucket = self._client.lookup_bucket(bucket_name=self._bucket_name)
        if self._bucket is None:
            self._client.close()
            raise ValueError(f"Bucket '{self._bucket_name}' does not exist.")

        self._redis = redis
        self._namespace = build_namespace(
            RESOURCE.aggregate(AggregateField.KEY),
            base=self._service_context.key,
            client=self._key,
            origin=CacheOrigin.CLIENT,
            layer=CacheLayer.SERVICE,
        )

        self._root_location = self._service_context.key

    @property
    def bucket(self) -> Bucket:
        if self._bucket is None:
            raise ValueError("Bucket has not been initialized.")
        return self._bucket

    async def upload(
        self,
        content: bytes,
        location: str,
        content_type: OptionalString = None,
        *,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
        root_location_override: OptionalString = None,
        make_public: bool = False,
        use_cache: bool = True,
        expiration: Expiration = Expiration.EXP_15MN,
    ) -> SingleDataResponse[Asset, None]:
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = CreateResourceOperationAction(
            type=ResourceOperationType.CREATE,
            create_type=ResourceOperationCreateType.NEW,
        )

        executed_at = datetime.now(tz=timezone.utc)

        if root_location_override is None or (
            isinstance(root_location_override, str) and len(root_location_override) <= 0
        ):
            blob_name = f"{self._root_location}/{location}"
        else:
            blob_name = f"{root_location_override}/{location}"

        resource = deepcopy(RESOURCE)
        resource.details = {"location": location, "blob_name": blob_name}

        try:
            blob = self.bucket.blob(blob_name=blob_name)
            blob.upload_from_string(content, content_type=content_type or "text/plain")

            if make_public:
                blob.make_public()
                url = blob.public_url
            else:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(seconds=expiration.value),
                    method="GET",
                )

            if use_cache:
                client = self._redis.client.get(Connection.ASYNC)
                cache_key = build_key(blob_name, namespace=self._namespace)
                await client.set(name=cache_key, value=url, ex=expiration.value)

            completed_at = datetime.now(tz=timezone.utc)

            asset = Asset(url=url)
            operation_response_data = DataPair[None, Asset](
                old=None,
                new=asset,
            )
            operation_response = CreateSingleDataResponse[Asset, None](
                data=operation_response_data, metadata=None, other=None
            )
            CreateSingleResourceOperation[Optional[GenericAuthentication], Asset, None](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary=f"Successfully uploaded object to '{location}'",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                resource=resource,
                response=operation_response,
            ).log(self._logger, Level.INFO)
            return SingleDataResponse[Asset, None](
                data=asset, metadata=None, other=None
            )
        except Exception as e:
            raise InternalServerError[Optional[GenericAuthentication]](
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary=f"Unexpected error raised while uploading object to '{location}'",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=resource,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            ) from e

    async def generate_signed_url(
        self,
        location: str,
        *,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
        root_location_override: OptionalString = None,
        use_cache: bool = True,
        expiration: Expiration = Expiration.EXP_15MN,
    ) -> SingleDataResponse[Asset, None]:
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = ReadResourceOperationAction()

        executed_at = datetime.now(tz=timezone.utc)

        if root_location_override is None or (
            isinstance(root_location_override, str) and len(root_location_override) <= 0
        ):
            blob_name = f"{self._root_location}/{location}"
        else:
            blob_name = f"{root_location_override}/{location}"

        resource = deepcopy(RESOURCE)
        resource.details = {"location": location, "blob_name": blob_name}

        if use_cache:
            client = self._redis.client.get(Connection.ASYNC)
            cache_key = build_key(blob_name, namespace=self._namespace)
            url = await client.get(cache_key)
            if url is not None:
                completed_at = datetime.now(tz=timezone.utc)
                operation_context = deepcopy(self._operation_context)
                operation_context.target.type = OperationTarget.CACHE
                asset = Asset(url=url)
                operation_response_data = DataPair[Asset, None](old=asset, new=None)
                operation_response = ReadSingleDataResponse[Asset, None](
                    data=operation_response_data, metadata=None, other=None
                )
                ReadSingleResourceOperation[
                    Optional[GenericAuthentication], Asset, None
                ](
                    service_context=self._service_context,
                    id=operation_id,
                    context=operation_context,
                    timestamp=OperationTimestamp(
                        executed_at=executed_at,
                        completed_at=completed_at,
                        duration=(completed_at - executed_at).total_seconds(),
                    ),
                    summary=f"Successfully retrieved signed url for '{location}' from cache",
                    request_context=request_context,
                    authentication=authentication,
                    action=operation_action,
                    resource=resource,
                    response=operation_response,
                ).log(
                    self._logger, Level.INFO
                )

                return SingleDataResponse[Asset, None](
                    data=asset, metadata=None, other=None
                )

        blob = self.bucket.blob(blob_name=blob_name)
        if not blob.exists():
            raise NotFound(
                OperationType.RESOURCE,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary=f"Asset '{location}' not found",
                request_context=request_context,
                authentication=authentication,
                resource=resource,
                operation_action=operation_action,
            )

        url = blob.generate_signed_url(
            version="v4", expiration=timedelta(seconds=expiration.value), method="GET"
        )

        if use_cache:
            client = self._redis.client.get(Connection.ASYNC)
            cache_key = build_key(blob_name, namespace=self._namespace)
            await client.set(name=cache_key, value=url, ex=expiration.value)

        completed_at = datetime.now(tz=timezone.utc)
        asset = Asset(url=url)
        operation_response_data = DataPair[Asset, None](old=asset, new=None)
        operation_response = ReadSingleDataResponse[Asset, None](
            data=operation_response_data, metadata=None, other=None
        )
        ReadSingleResourceOperation[Optional[GenericAuthentication], Asset, None](
            service_context=self._service_context,
            id=operation_id,
            context=self._operation_context,
            timestamp=OperationTimestamp(
                executed_at=executed_at,
                completed_at=completed_at,
                duration=(completed_at - executed_at).total_seconds(),
            ),
            summary=f"Successfully generated signed url for asset '{location}'",
            request_context=request_context,
            authentication=authentication,
            action=operation_action,
            resource=resource,
            response=operation_response,
        ).log(self._logger, Level.INFO)

        return SingleDataResponse[Asset, None](data=asset, metadata=None, other=None)
