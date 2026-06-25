"""Single source of truth for pipeline version constants.

Bump PIPELINE_VERSION on every release that changes decision behavior.
REQUIREMENT_SCHEMA_VERSION tracks the requirement.schema.json contract version.
Both are recorded in every ExtractionResult so that archived outputs can be
reproduced or compared against future runs.
"""

PIPELINE_VERSION = "v0.1.0"
REQUIREMENT_SCHEMA_VERSION = "1.1"  # matches current requirement.schema.json
