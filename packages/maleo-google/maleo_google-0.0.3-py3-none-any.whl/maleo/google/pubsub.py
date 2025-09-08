from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, Optional, TypeVar
from maleo.types.controllers.message import ReturnT, MessageController


class TopicConfig(BaseModel):
    id: str = Field(..., description="Topic's id")


DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="database-operation")
DEFAULT_REQUEST_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="request-operation")
DEFAULT_RESOURCE_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="resource-operation")
DEFAULT_SYSTEM_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="system-operation")
DEFAULT_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="operation")
DEFAULT_RESOURCE_MEASUREMENT_TOPIC_CONFIGURATION = TopicConfig(
    id="resource-measurement"
)


class TopicsConfig(BaseModel):
    database_operation: TopicConfig = Field(
        default=DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATION,
        description="Database operation topic configurations",
    )
    request_operation: TopicConfig = Field(
        default=DEFAULT_REQUEST_OPERATION_TOPIC_CONFIGURATION,
        description="Request operation topic configurations",
    )
    resource_operation: TopicConfig = Field(
        default=DEFAULT_RESOURCE_OPERATION_TOPIC_CONFIGURATION,
        description="Resource operation topic configurations",
    )
    system_operation: TopicConfig = Field(
        default=DEFAULT_SYSTEM_OPERATION_TOPIC_CONFIGURATION,
        description="System operation topic configurations",
    )
    operation: TopicConfig = Field(
        default=DEFAULT_OPERATION_TOPIC_CONFIGURATION,
        description="Operation topic configurations",
    )
    resource_measurement: TopicConfig = Field(
        default=DEFAULT_RESOURCE_MEASUREMENT_TOPIC_CONFIGURATION,
        description="Resource measurement topic configurations",
    )


TopicsConfigT = TypeVar("TopicsConfigT", bound=TopicsConfig)


class PublisherConfig(BaseModel, Generic[TopicsConfigT]):
    topics: TopicsConfigT = Field(..., description="Topics configurations")


class SubscriptionConfig(BaseModel):
    id: str = Field(..., description="Subscription's ID")
    max_messages: int = Field(10, description="Subscription's Max messages")
    ack_deadline: int = Field(10, description="Subscription's ACK deadline")


class ExtendedSubscriptionConfig(SubscriptionConfig, Generic[ReturnT]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    controller: Optional[MessageController[ReturnT]] = Field(
        None, description="Optional message controller"
    )


SubscriptionsConfigT = TypeVar("SubscriptionsConfigT", bound=Optional[BaseModel])


class Config(BaseModel, Generic[TopicsConfigT, SubscriptionsConfigT]):
    publisher: PublisherConfig[TopicsConfigT] = Field(
        ...,
        description="Publisher's configurations",
    )
    subscriptions: Optional[SubscriptionsConfigT] = Field(
        None, description="Subscriptions's configurations"
    )


ConfigT = TypeVar("ConfigT", bound=Config)


class ConfigMixin(BaseModel, Generic[ConfigT]):
    pubsub: ConfigT = Field(..., description="PubSub configuration")
