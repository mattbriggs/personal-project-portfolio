"""Shared contract primitives."""

from pydantic import BaseModel


class OkResponse(BaseModel):
    """Generic success acknowledgement for operations without a body.

    :param ok: Always ``True``.
    """

    ok: bool = True


class RestartRequiredResponse(BaseModel):
    """Acknowledgement that also reports whether a restart is required.

    :param ok: Always ``True``.
    :param restart_required: ``True`` when a setting change needs a restart.
    """

    ok: bool = True
    restart_required: bool = False
