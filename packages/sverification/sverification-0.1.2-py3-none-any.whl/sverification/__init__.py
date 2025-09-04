"""
Statement Verification Package

A tool for verifying PDF statements by checking metadata and other attributes.
"""

__version__ = "0.1.0"

# Import main functions for easier access
from .compare_metadata import extract_all, compare_fields, load_brands, verify_statement_verbose, print_verification_report, load_font_data, compare_font_data
from .pdf_name_extractor import get_company_name
from .font_data_extractor import extract_pdf_font_data

__all__ = [
    "extract_all",
    "compare_fields", 
    "load_brands",
    "load_font_data",
    "compare_font_data",
    "get_company_name",
    "verify_statement_verbose",
    "print_verification_report",
    "extract_pdf_font_data"
]