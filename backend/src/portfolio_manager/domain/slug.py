"""Slug generation.

Ported verbatim from the original ``ProjectService._slugify`` so slugs derived
from project names match existing data. Slug uniqueness is enforced at the
database level; the current behavior is *rejection* on collision (see
:class:`portfolio_manager.application.services.project_service.ProjectService`),
not numeric suffixing.
"""

import re


def slugify(name: str) -> str:
    """Convert a project name to a URL-safe slug.

    :param name: Human-readable project name.
    :returns: Lowercase slug with hyphens replacing whitespace/punctuation.
    :rtype: str
    """
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug
