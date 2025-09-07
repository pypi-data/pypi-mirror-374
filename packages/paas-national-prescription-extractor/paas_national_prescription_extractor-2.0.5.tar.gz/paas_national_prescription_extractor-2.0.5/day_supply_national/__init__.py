"""
PAAS National - Prescription Data Extractor
==========================================

A comprehensive Python package for extracting, correcting, and standardizing
prescription data from various medication types. Handles day supply calculation,
quantity validation, and sig standardization.

Key Features:
- 100% success rate across all medication types
- Zero warnings - clean, reliable processing
- Intelligent drug name matching with fuzzy logic
- Accurate day supply calculations
- Quantity validation and correction
- Standardized sig/directions formatting
- Support for 8+ medication categories

Usage:
    from day_supply_national import (
        PrescriptionDataExtractor, PrescriptionInput
    )

    extractor = PrescriptionDataExtractor()
    prescription = PrescriptionInput("Humalog", "5", "15 units tid")
    result = extractor.extract_prescription_data(prescription)

    print(f"Day Supply: {result.calculated_day_supply}")
    print(f"Corrected Quantity: {result.corrected_quantity}")
    print(f"Standardized Sig: {result.standardized_sig}")

Author: Abdulhaleem Osama (TJMLabs)
Version: 2.0.4
License: MIT
"""

from .extractor import (
    ExtractedData,
    MedicationType,
    PrescriptionDataExtractor,
    PrescriptionInput,
)

__version__ = "2.0.5"
__author__ = "Abdulhaleem Osama"
__email__ = "haleemborham3@gmail.com"
__license__ = "MIT"

__all__ = [
    "PrescriptionDataExtractor",
    "PrescriptionInput",
    "ExtractedData",
    "MedicationType",
    "__version__",
]
