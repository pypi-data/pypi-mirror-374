"""
Good Common Types Module

This module provides type definitions and utilities, with optimized lazy loading
for heavy dependencies to improve import performance.
"""

import typing
from typing import TYPE_CHECKING

# Lazy imports - these will be loaded on first use
_URL = None
_Domain = None
_to_url = None
_Identifier = None

# Always imported (lightweight)
from .placeholder import placeholder
from ._base import StringDict, PythonImportableObject
from ._fields import (
    UUID,
    UUIDField,
    StringDictField,
    DateTimeField,
    VALID_ZIP_CODE,
    UPPER_CASE_STRING,
)

if TYPE_CHECKING:
    # For type checking, import everything
    from .web import URL as _URLType, Domain as _DomainType, to_url as _to_url_func
    from ._base import Identifier as _IdentifierType
    
    URL = _URLType
    Domain = _DomainType
    to_url = _to_url_func
    Identifier = _IdentifierType
else:
    # Runtime lazy loading implementation
    def __getattr__(name: str) -> typing.Any:
        """Lazy load heavy modules on first access."""
        global _URL, _Domain, _to_url, _Identifier
        
        if name == "URL":
            if _URL is None:
                from .web import URL as _URL
            return _URL
        elif name == "Domain":
            if _Domain is None:
                from .web import Domain as _Domain
            return _Domain
        elif name == "to_url":
            if _to_url is None:
                from .web import to_url as _to_url
            return _to_url
        elif name == "Identifier":
            if _Identifier is None:
                from ._base import Identifier as _Identifier
            return _Identifier
        else:
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "UUID",
    "URL",
    "Domain",
    "to_url",
    "placeholder",
    "UUIDField",
    "StringDictField", 
    "DateTimeField",
    "VALID_ZIP_CODE",
    "UPPER_CASE_STRING",
    "StringDict",
    "Identifier",
    "PythonImportableObject",
]