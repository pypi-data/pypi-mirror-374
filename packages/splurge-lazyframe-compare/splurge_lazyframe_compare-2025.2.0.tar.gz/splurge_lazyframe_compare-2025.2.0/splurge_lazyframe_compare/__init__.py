"""Polars LazyFrame Comparison Framework.

A comprehensive Python framework for comparing two Polars LazyFrames with
configurable schemas, primary keys, and column mappings.

Copyright (c) 2025 Jim Schilling.
Licensed under the MIT License. See the LICENSE file for details.
"""

# Service-based architecture
from .core.comparator import ComparisonReport, LazyFrameComparator
from .models.comparison import ComparisonResult, ComparisonSummary
from .models.schema import (
    ColumnDefinition,
    ColumnMapping,
    ComparisonConfig,
    ComparisonSchema,
)
from .models.validation import ValidationResult
from .services import (
    ComparisonService,
    DataPreparationService,
    ReportingService,
    ValidationService,
)
from .services.orchestrator import ComparisonOrchestrator

__version__ = "2025.2.0"

__all__ = [
    # Service-based architecture
    "LazyFrameComparator",
    "ComparisonReport",
    "ComparisonResult",
    "ComparisonSummary",
    "ComparisonConfig",
    "ComparisonSchema",
    "ColumnDefinition",
    "ColumnMapping",
    "ValidationResult",
    "ComparisonOrchestrator",
    "ComparisonService",
    "DataPreparationService",
    "ReportingService",
    "ValidationService",
]
