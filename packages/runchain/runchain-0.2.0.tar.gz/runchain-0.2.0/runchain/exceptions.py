from __future__ import annotations

from click import ClickException


class RunchainException(ClickException):
    """Base exception for all runchain errors."""

    pass


class ChainError(RunchainException):
    """Exception raised for chain-related errors."""

    pass
