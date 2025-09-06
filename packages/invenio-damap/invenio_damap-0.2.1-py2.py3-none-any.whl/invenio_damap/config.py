# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
# Copyright (C) 2024 TU Wien.
#
# Invenio-DAMAP is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-DAMAP configuration for InvenioRDM."""

from .fetchers import custom_header_fetcher
from .generators import default_namespaced_id_generator

DAMAP_BASE_URL = "http://localhost:8085"
"""The base URL for the DAMAP server."""

DAMAP_CUSTOM_HEADER_FUNCTION = custom_header_fetcher
"""Default function used to define additional headers for HTTP requests to DAMAP."""

DAMAP_INTEGRATION_ENABLED = False
"""Flag to determine whether the DAMAP integration is enabled."""

DAMAP_DMP_DATASET_DISTRIBUTION_HOST = {
    "availability": None,
    "backup_frequency": None,
    "backup_type": None,
    "certified_with": None,
    "description": None,
    "geo_location": None,
    "pid_system": None,
    "storage_type": None,
    "support_versioning": None,
}
"""A dictionary containing metadata attributes for dataset distribution hosts in DAMAP.
Depends on the specific InvenioRDM instance, so each attribute must be modified accordingly.
"""

DAMAP_JWT_ENCODE_ALGORITHM = "HS256"
"""The symmetric algorithm used for encoding JWTs for communication between InvenioRDM and DAMAP."""

DAMAP_PERSON_FUNCTION = default_namespaced_id_generator
"""Default function used to identify a user between InvenioRDM and DAMAP."""

DAMAP_SHARED_SECRET = "thisIsAVerySecretKeyOfAtLeast32Chars"
"""The shared secret or token used for secure communication with DAMAP."""
