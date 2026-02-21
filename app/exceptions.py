from __future__ import annotations


class FleetBiteError(Exception):
    """Base exception for all FleetBite domain errors."""
    pass


class UserNotFoundError(FleetBiteError):
    pass


class DuplicateEmailError(FleetBiteError):
    pass


class InvalidCredentialsError(FleetBiteError):
    pass


class InactiveUserError(FleetBiteError):
    pass
