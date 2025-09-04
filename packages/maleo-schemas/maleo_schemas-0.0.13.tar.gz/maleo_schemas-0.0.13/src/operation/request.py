from typing import Generic, Literal, Optional, Union, overload
from uuid import UUID
from maleo.dtos.authentication import AuthenticationT
from maleo.dtos.error import GenericErrorT, ErrorT
from maleo.dtos.contexts.operation import OperationContext
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.response import ResponseContext
from maleo.dtos.contexts.service import ServiceContext
from maleo.enums.operation import (
    OperationType,
    ResourceOperationType,
    ResourceOperationCreateType,
    ResourceOperationUpdateType,
    ResourceOperationDataUpdateType,
    ResourceOperationStatusUpdateType,
)
from maleo.mixins.general import SuccessT
from maleo.mixins.timestamp import OperationTimestamp
from ..response import ResponseT, ErrorResponseT, SuccessResponseT
from .base import BaseOperation
from .resource import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    AllResourceOperationAction,
    ResourceOperationActionT,
    generate_resource_operation_action,
)


class RequestOperation(
    BaseOperation[
        None,
        SuccessT,
        GenericErrorT,
        Optional[RequestContext],
        AuthenticationT,
        ResourceOperationActionT,
        Optional[ResponseContext],
        ResponseT,
    ],
    Generic[
        SuccessT,
        GenericErrorT,
        AuthenticationT,
        ResourceOperationActionT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.REQUEST
    resource: None = None


class FailedRequestOperation(
    RequestOperation[
        Literal[False],
        ErrorT,
        AuthenticationT,
        ResourceOperationActionT,
        ErrorResponseT,
    ],
    Generic[
        ErrorT,
        AuthenticationT,
        ResourceOperationActionT,
        ErrorResponseT,
    ],
):
    success: Literal[False] = False
    summary: str = "Failed processing request"


class CreateFailedRequestOperation(
    FailedRequestOperation[
        ErrorT, AuthenticationT, CreateResourceOperationAction, ErrorResponseT
    ],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


class ReadFailedRequestOperation(
    FailedRequestOperation[
        ErrorT, AuthenticationT, ReadResourceOperationAction, ErrorResponseT
    ],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


class UpdateFailedRequestOperation(
    FailedRequestOperation[
        ErrorT, AuthenticationT, UpdateResourceOperationAction, ErrorResponseT
    ],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


class DeleteFailedRequestOperation(
    FailedRequestOperation[
        ErrorT, AuthenticationT, DeleteResourceOperationAction, ErrorResponseT
    ],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


@overload
def generate_failed_request_operation(
    action: CreateResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> CreateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_request_operation(
    action: ReadResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> ReadFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_request_operation(
    action: UpdateResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> UpdateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_request_operation(
    action: DeleteResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> DeleteFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_request_operation(
    *,
    type: Literal[ResourceOperationType.CREATE],
    create_type: Optional[ResourceOperationCreateType] = ...,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> CreateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_request_operation(
    *,
    type: Literal[ResourceOperationType.READ],
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> ReadFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_request_operation(
    *,
    type: Literal[ResourceOperationType.UPDATE],
    update_type: Optional[ResourceOperationUpdateType] = ...,
    data_update_type: Optional[ResourceOperationDataUpdateType] = ...,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = ...,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> UpdateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_request_operation(
    *,
    type: Literal[ResourceOperationType.DELETE],
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> DeleteFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
def generate_failed_request_operation(
    action: Optional[AllResourceOperationAction] = None,
    *,
    type: Optional[ResourceOperationType] = None,
    create_type: Optional[ResourceOperationCreateType] = None,
    update_type: Optional[ResourceOperationUpdateType] = None,
    data_update_type: Optional[ResourceOperationDataUpdateType] = None,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    response_context: Optional[ResponseContext],
    response: ErrorResponseT,
) -> Union[
    CreateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
    ReadFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
    UpdateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
    DeleteFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
]:
    if (action is None and type is None) or (action is not None and type is not None):
        raise ValueError("Only either 'action' or 'type' must be given")

    if action is not None:
        if not isinstance(
            action,
            (
                CreateResourceOperationAction,
                ReadResourceOperationAction,
                UpdateResourceOperationAction,
                DeleteResourceOperationAction,
            ),
        ):
            raise ValueError(f"Invalid 'action' type: '{type(action)}'")

        if isinstance(action, CreateResourceOperationAction):
            return CreateFailedRequestOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response_context=response_context,
                response=response,
            )
        elif isinstance(action, ReadResourceOperationAction):
            return ReadFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response_context=response_context,
                response=response,
            )
        elif isinstance(action, UpdateResourceOperationAction):
            return UpdateFailedRequestOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response_context=response_context,
                response=response,
            )
        elif isinstance(action, DeleteResourceOperationAction):
            return DeleteFailedRequestOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response_context=response_context,
                response=response,
            )

    elif type is not None:
        if not isinstance(type, ResourceOperationType):
            raise ValueError(f"Unsupported `type`: {type}")

        if type is ResourceOperationType.CREATE:
            action = generate_resource_operation_action(
                type=type, create_type=create_type
            )
            return CreateFailedRequestOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response_context=response_context,
                response=response,
            )
        elif type is ResourceOperationType.READ:
            action = generate_resource_operation_action(type=type)
            return ReadFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response_context=response_context,
                response=response,
            )
        elif type is ResourceOperationType.UPDATE:
            action = generate_resource_operation_action(
                type=type,
                update_type=update_type,
                data_update_type=data_update_type,
                status_update_type=status_update_type,
            )
            return UpdateFailedRequestOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response_context=response_context,
                response=response,
            )
        elif type is ResourceOperationType.DELETE:
            action = generate_resource_operation_action(type=type)
            return DeleteFailedRequestOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response_context=response_context,
                response=response,
            )
    else:
        # This should never happen due to initial validation,
        # but type checker needs to see all paths covered
        raise ValueError("Neither 'action' nor 'type' provided")


class SuccessfulRequestOperation(
    RequestOperation[
        Literal[True],
        None,
        AuthenticationT,
        ResourceOperationActionT,
        SuccessResponseT,
    ],
    Generic[
        AuthenticationT,
        ResourceOperationActionT,
        SuccessResponseT,
    ],
):
    success: Literal[True] = True
    error: None = None
    summary: str = "Successfully processed request"


class CreateSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        AuthenticationT, CreateResourceOperationAction, SuccessResponseT
    ],
    Generic[AuthenticationT, SuccessResponseT],
):
    pass


class ReadSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        AuthenticationT, ReadResourceOperationAction, SuccessResponseT
    ],
    Generic[AuthenticationT, SuccessResponseT],
):
    pass


class UpdateSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        AuthenticationT, UpdateResourceOperationAction, SuccessResponseT
    ],
    Generic[AuthenticationT, SuccessResponseT],
):
    pass


class DeleteSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        AuthenticationT, DeleteResourceOperationAction, SuccessResponseT
    ],
    Generic[AuthenticationT, SuccessResponseT],
):
    pass
