"""Compatibility entry point for the installed Lotus principal runtime.

Install packages/principal-authority first. There is no source-path fallback or
fixture-derived trust configuration.
"""

from lotus_principal_authority.verifier import *  # noqa: F403
from lotus_principal_authority.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
