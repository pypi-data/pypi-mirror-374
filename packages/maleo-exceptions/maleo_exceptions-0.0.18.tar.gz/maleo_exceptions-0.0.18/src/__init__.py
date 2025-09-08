import traceback as tb
from typing import Dict, Generic, Literal, Optional, Tuple, Type, Union, overload
from uuid import UUID, uuid4
from maleo.dtos.authentication import AuthenticationT
from maleo.dtos.contexts.operation import OperationContext
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.response import ResponseContext
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.error import (
    ErrorT,
    Error,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    MethodNotAllowedError,
    ConflictError,
    UnprocessableEntityError,
    TooManyRequestsError,
    InternalServerError as InternalServerErrorSchema,
    DatabaseError as DatabaseErrorSchema,
    NotImplementedError,
    BadGatewayError,
    ServiceUnavailableError,
)
from maleo.dtos.error.metadata import ErrorMetadata
from maleo.dtos.error.spec import (
    ErrorSpecT,
    ErrorSpec,
    BadRequestErrorSpec,
    UnauthorizedErrorSpec,
    ForbiddenErrorSpec,
    NotFoundErrorSpec,
    MethodNotAllowedErrorSpec,
    ConflictErrorSpec,
    UnprocessableEntityErrorSpec,
    TooManyRequestsErrorSpec,
    InternalServerErrorSpec,
    DatabaseErrorSpec,
    NotImplementedErrorSpec,
    BadGatewayErrorSpec,
    ServiceUnavailableErrorSpec,
)
from maleo.dtos.resource import AggregateField, Resource
from maleo.enums.error import Code as ErrorCode
from maleo.enums.operation import OperationType
from maleo.logging.enums import Level
from maleo.logging.logger import Exception as ExceptionLogger
from maleo.mixins.timestamp import OperationTimestamp
from maleo.schemas.operation.request import (
    CreateFailedRequestOperation,
    ReadFailedRequestOperation,
    UpdateFailedRequestOperation,
    DeleteFailedRequestOperation,
    generate_failed_request_operation,
)
from maleo.schemas.operation.resource import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    AllResourceOperationAction,
    CreateFailedResourceOperation,
    ReadFailedResourceOperation,
    UpdateFailedResourceOperation,
    DeleteFailedResourceOperation,
    generate_failed_resource_operation,
)
from maleo.schemas.operation.system import SystemOperationAction, FailedSystemOperation
from maleo.schemas.response import (
    ErrorResponseT,
    ErrorResponse,
    BadRequestResponse,
    UnauthorizedResponse,
    ForbiddenResponse,
    NotFoundResponse,
    MethodNotAllowedResponse,
    ConflictResponse,
    UnprocessableEntityResponse,
    TooManyRequestsResponse,
    InternalServerErrorResponse,
    DatabaseErrorResponse,
    NotImplementedResponse,
    BadGatewayResponse,
    ServiceUnavailableResponse,
)
from maleo.types.base.any import OptionalAny
from maleo.types.base.string import ListOfStrings
from maleo.types.base.uuid import OptionalUUID


class MaleoException(
    Exception,
    Generic[
        AuthenticationT,
        ErrorSpecT,
        ErrorT,
        ErrorResponseT,
    ],
):
    error_spec_cls: Type[ErrorSpecT]
    error_cls: Type[ErrorT]
    response_cls: Type[ErrorResponseT]

    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.REQUEST],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "Request operation failed due to exception being raised",
        operation_action: AllResourceOperationAction,
        request_context: RequestContext,
        authentication: AuthenticationT,
        details: OptionalAny = None,
        response_context: Optional[ResponseContext] = None,
        response: Optional[ErrorResponseT] = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.RESOURCE],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "Resource operation failed due to exception being raised",
        operation_action: AllResourceOperationAction,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        resource: Resource,
        details: OptionalAny = None,
        response: Optional[ErrorResponseT] = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.SYSTEM],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "System operation failed due to exception being raised",
        operation_action: SystemOperationAction,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        details: OptionalAny = None,
        response: Optional[ErrorResponseT] = None,
    ) -> None: ...
    def __init__(
        self,
        operation_type: OperationType,
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "Operation failed due to exception being raised",
        operation_action: Union[SystemOperationAction, AllResourceOperationAction],
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        resource: Optional[Resource] = None,
        details: OptionalAny = None,
        response_context: Optional[ResponseContext] = None,
        response: Optional[ErrorResponseT] = None,
    ) -> None:
        super().__init__(*args)

        self.operation_type = operation_type

        self.service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        self.operation_id = operation_id if operation_id is not None else uuid4()
        self.operation_context = operation_context

        self.operation_timestamp = (
            operation_timestamp
            if operation_timestamp is not None
            else OperationTimestamp.now()
        )

        self.operation_summary = operation_summary
        self.request_context = request_context
        self.authentication = authentication
        self.operation_action = operation_action
        self.resource = resource
        self.details = details
        self.response_context = response_context
        self._response = response

    @property
    def error_spec(self) -> ErrorSpecT:
        # * This line will not break due to the error spec
        # * field's being already given a default value
        return self.error_spec_cls()  # type: ignore

    @property
    def traceback(self) -> ListOfStrings:
        return tb.format_exception(self)

    @property
    def error_metadata(self) -> ErrorMetadata:
        return ErrorMetadata(details=self.details, traceback=self.traceback)

    @property
    def error(self) -> ErrorT:
        return self.error_cls.model_validate(
            {**self.error_spec.model_dump(), **self.error_metadata.model_dump()}
        )

    @property
    def response(self) -> ErrorResponseT:
        if self._response is not None:
            if self._response.other is None:
                self._response.other = self.details
            return self._response

        # * This line will not break due to the error spec
        # * field's being already given a default value
        return self.response_cls(other=self.details)  # type: ignore

    @overload
    def generate_operation(
        self, operation_type: Literal[OperationType.REQUEST]
    ) -> Union[
        CreateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
        ReadFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
        UpdateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
        DeleteFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
    ]: ...
    @overload
    def generate_operation(
        self, operation_type: Literal[OperationType.RESOURCE]
    ) -> Union[
        CreateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        ReadFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        UpdateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        DeleteFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
    ]: ...
    @overload
    def generate_operation(
        self, operation_type: Literal[OperationType.SYSTEM]
    ) -> FailedSystemOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
    def generate_operation(self, operation_type: OperationType) -> Union[
        CreateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
        ReadFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
        UpdateFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
        DeleteFailedRequestOperation[ErrorT, AuthenticationT, ErrorResponseT],
        CreateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        ReadFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        UpdateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        DeleteFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        FailedSystemOperation[ErrorT, AuthenticationT, ErrorResponseT],
    ]:
        if operation_type != self.operation_type:
            raise ValueError(
                ErrorCode.INTERNAL_SERVER_ERROR,
                f"Mismatched 'operation_type': '{self.operation_type}'",
            )

        if self.operation_type not in OperationType:
            raise ValueError(
                ErrorCode.INTERNAL_SERVER_ERROR,
                f"Invalid 'operation_type': '{self.operation_type}'",
            )

        if self.operation_type is OperationType.SYSTEM:
            if not isinstance(self.operation_action, SystemOperationAction):
                raise TypeError(
                    f"Invalid type for 'operation_action': {type(self.operation_action)}"
                )
            return FailedSystemOperation[ErrorT, AuthenticationT, ErrorResponseT](
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary="Failed system operation",
                error=self.error,
                request_context=self.request_context,
                authentication=self.authentication,
                action=self.operation_action,
                response=self.response,
            )

        elif self.operation_type is OperationType.REQUEST:
            if not isinstance(
                self.operation_action,
                (
                    CreateResourceOperationAction,
                    ReadResourceOperationAction,
                    UpdateResourceOperationAction,
                    DeleteResourceOperationAction,
                ),
            ):
                raise TypeError(
                    f"Invalid type for 'operation_action': {type(self.operation_action)}"
                )

            return generate_failed_request_operation(
                action=self.operation_action,
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary=self.operation_summary,
                error=self.error,
                request_context=self.request_context,
                authentication=self.authentication,
                response_context=self.response_context,
                response=self.response,
            )

        elif self.operation_type is OperationType.RESOURCE:
            if not isinstance(
                self.operation_action,
                (
                    CreateResourceOperationAction,
                    ReadResourceOperationAction,
                    UpdateResourceOperationAction,
                    DeleteResourceOperationAction,
                ),
            ):
                raise TypeError(
                    f"Invalid type for 'operation_action': {type(self.operation_action)}"
                )

            if self.resource is None:
                raise ValueError(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Resource must be given for resource operation exception",
                )

            return generate_failed_resource_operation(
                action=self.operation_action,
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary=self.operation_summary,
                error=self.error,
                request_context=self.request_context,
                authentication=self.authentication,
                resource=self.resource,
                response=self.response,
            )

        else:
            # This should never happen due to the first check, but makes the function exhaustive
            raise ValueError(
                ErrorCode.INTERNAL_SERVER_ERROR,
                f"Unhandled operation_type: '{self.operation_type}'",
            )


class ClientException(
    MaleoException[
        AuthenticationT,
        ErrorSpecT,
        ErrorT,
        ErrorResponseT,
    ],
    Generic[
        AuthenticationT,
        ErrorSpecT,
        ErrorT,
        ErrorResponseT,
    ],
):
    """Base class for all client error (HTTP 4xx) responses"""


class BadRequest(
    ClientException[
        AuthenticationT,
        BadRequestErrorSpec,
        BadRequestError,
        BadRequestResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class Unauthorized(
    ClientException[
        AuthenticationT,
        UnauthorizedErrorSpec,
        UnauthorizedError,
        UnauthorizedResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class Forbidden(
    ClientException[
        AuthenticationT,
        ForbiddenErrorSpec,
        ForbiddenError,
        ForbiddenResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class NotFound(
    ClientException[
        AuthenticationT,
        NotFoundErrorSpec,
        NotFoundError,
        NotFoundResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class MethodNotAllowed(
    ClientException[
        AuthenticationT,
        MethodNotAllowedErrorSpec,
        MethodNotAllowedError,
        MethodNotAllowedResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class Conflict(
    ClientException[
        AuthenticationT,
        ConflictErrorSpec,
        ConflictError,
        ConflictResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class UnprocessableEntity(
    ClientException[
        AuthenticationT,
        UnprocessableEntityErrorSpec,
        UnprocessableEntityError,
        UnprocessableEntityResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class TooManyRequests(
    ClientException[
        AuthenticationT,
        TooManyRequestsErrorSpec,
        TooManyRequestsError,
        TooManyRequestsResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class ServerException(
    MaleoException[
        AuthenticationT,
        ErrorSpecT,
        ErrorT,
        ErrorResponseT,
    ],
    Generic[
        AuthenticationT,
        ErrorSpecT,
        ErrorT,
        ErrorResponseT,
    ],
):
    """Base class for all server error (HTTP 5xx) responses"""


class InternalServerError(
    ServerException[
        AuthenticationT,
        InternalServerErrorSpec,
        InternalServerErrorSchema,
        InternalServerErrorResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class DatabaseError(
    ServerException[
        AuthenticationT,
        DatabaseErrorSpec,
        DatabaseErrorSchema,
        DatabaseErrorResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class NotImplemented(
    ServerException[
        AuthenticationT,
        NotImplementedErrorSpec,
        NotImplementedError,
        NotImplementedResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class BadGateway(
    ServerException[
        AuthenticationT,
        BadGatewayErrorSpec,
        BadGatewayError,
        BadGatewayResponse,
    ],
    Generic[AuthenticationT],
):
    pass


class ServiceUnavailable(
    ServerException[
        AuthenticationT,
        ServiceUnavailableErrorSpec,
        ServiceUnavailableError,
        ServiceUnavailableResponse,
    ],
    Generic[AuthenticationT],
):
    pass


def from_resource_http_request(
    status_code: int,
    service_context: Optional[ServiceContext],
    operation_id: UUID,
    operation_context: OperationContext,
    operation_timestamp: OperationTimestamp,
    operation_action: AllResourceOperationAction,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    logger: ExceptionLogger,
) -> MaleoException[AuthenticationT, ErrorSpec, Error, ErrorResponse]:
    """Create appropriate error based on HTTP status code"""

    # * We are ignoring this type because we are sure that this is already proper
    error_mapping: Dict[
        int,
        Tuple[
            Type[MaleoException[AuthenticationT, ErrorSpec, Error, ErrorResponse]], str
        ],
    ] = {
        400: (
            BadRequest[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Bad Request response",
        ),
        401: (
            Unauthorized[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Unauthorized response",
        ),
        403: (
            Forbidden[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Forbidden response",
        ),
        404: (
            NotFound[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Not Found response",
        ),
        405: (
            MethodNotAllowed[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Method Not Allowed response",
        ),
        409: (
            Conflict[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Conflict response",
        ),
        422: (
            UnprocessableEntity[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Unprocessable Entity response",
        ),
        429: (
            TooManyRequests[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Too Many Requests response",
        ),
        500: (
            InternalServerError[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Internal Server Error response",
        ),
        501: (
            NotImplemented[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Not Implemented response",
        ),
        502: (
            BadGateway[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Bad Gateway response",
        ),
        503: (
            ServiceUnavailable[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to Service Unavailable response",
        ),
    }  # type: ignore

    error_class, summary = error_mapping.get(
        status_code,
        (
            InternalServerError[AuthenticationT],
            f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to unexpected error",
        ),
    )

    error = error_class(
        OperationType.RESOURCE,
        service_context=service_context,
        operation_id=operation_id,
        operation_context=operation_context,
        operation_timestamp=operation_timestamp,
        operation_summary=summary,
        operation_action=operation_action,
        request_context=request_context,
        authentication=authentication,
        resource=resource,
    )

    operation = error.generate_operation(OperationType.RESOURCE)
    operation.log(logger, Level.ERROR)

    return error  # type: ignore
