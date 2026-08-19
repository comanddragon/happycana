# =============================================================================
# core/validators.py
# =============================================================================
from django.core.exceptions import ValidationError
import re


def validate_phone(value):
    pattern = re.compile(r"^\+?1?\d{9,15}$")
    if not pattern.match(value):
        raise ValidationError(f"{value} is not a valid phone number. Use E.164 format e.g. +1234567890.")


def validate_positive_decimal(value):
    if value <= 0:
        raise ValidationError("Value must be greater than zero.")


