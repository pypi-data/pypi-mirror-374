"""
Sistema de respuestas estandarizadas para tai-api.

Este módulo proporciona clases para manejar respuestas exitosas y de error
de manera consistente en toda la API.
"""
# Importar excepciones y manejadores
from .exceptions import (
    ErrorCode,
    APIException,
    ValidationException,
    RecordNotFoundException,
    DatabaseException,
    DuplicateRecordException,
    ForeignKeyViolationException,
    BusinessRuleViolationException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
    SessionInvalidatedException,
    SessionExpiredException,
    ConcurrentSessionDetectedException
)
from .responses import (
    APIResponse,
    APIError,
    PaginationMeta,
    ResponseStatus,
    PaginatedResponse
)

from .decorators import (
    document_api_response,
    document_paginated_response
)

from .handlers import setup_exception_handlers

from .mcp import set_mcp

__all__ = [
    # Clases de respuesta
    "ResponseStatus",
    "APIError",
    "PaginationMeta",
    "APIResponse",
    "PaginatedResponse",
    
    # Decoradores de documentación
    "document_api_response",
    "document_paginated_response",
    
    # Excepciones
    "APIException",
    "ErrorCode", 
    "ValidationException", 
    "RecordNotFoundException",
    "DatabaseException",
    "DuplicateRecordException",
    "ForeignKeyViolationException",
    "BusinessRuleViolationException",
    "InvalidCredentialsException",
    "InvalidTokenException",
    "TokenExpiredException", 
    "SessionInvalidatedException",
    "SessionExpiredException",
    "ConcurrentSessionDetectedException",
    
    # Manejadores
    "setup_exception_handlers",
    
    # MCP
    "set_mcp"
]
