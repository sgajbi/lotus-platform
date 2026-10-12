"""One fixture-independent verifier; identity providers remain deployment inputs."""

from .verifier import (
    Denial,
    GrantSet,
    GrantStoreUnavailable,
    PrincipalAdmission,
    ResolvedPrincipal,
    VerificationInputs,
    resolve_admission,
    resolve_principal,
    verify_credential,
)

__all__ = [
    "Denial", "GrantSet", "GrantStoreUnavailable", "PrincipalAdmission",
    "ResolvedPrincipal", "VerificationInputs", "resolve_admission",
    "resolve_principal", "verify_credential",
]
