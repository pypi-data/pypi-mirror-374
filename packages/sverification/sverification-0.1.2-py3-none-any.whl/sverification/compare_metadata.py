#!/usr/bin/env python3
"""
pdf_brand_checker.py

Usage:
  python pdf_brand_checker.py /path/to/file.pdf \
      --brands /path/to/statements_metadata.json \
      

What it does:
1) Detects the brand using the provided get_company_name() from pdf_name_extractor.py.
2) Extracts PDF metadata / internals using pdforensic:
   - extract_pdf_metadata
   - recover_pdf_versions
   - count_pdf_eof_markers
   - check_no_of_versions
3) Loads the brand "ground-truth" from statements_metadata.json and compares against
   the extracted values. Outputs a per-field match report and an overall
   percentage score.

Notes:
- Only non-empty expected fields in statements_metadata.json are scored.
- String comparisons are case-insensitive and trimmed.
- Numeric fields are compared as integers when possible.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple

# Ensure we can import the user's pdf_name_extractor.py sitting next to this script
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

try:
    from pdf_name_extractor import get_company_name  # provided by user
    from font_data_extractor import extract_pdf_font_data  # font extraction functionality
except Exception as e:
    raise SystemExit(f"Failed to import from pdf_name_extractor.py or font_data_extractor.py: {e}")

# pdforensic imports (must be installed in the environment where you run this script)
try:
    from pdforensic import (
        extract_pdf_metadata,
        recover_pdf_versions,
        count_pdf_eof_markers,
        check_no_of_versions
    )
except Exception as e:
    raise SystemExit(
        "Failed to import pdforensic. Please install it in your environment "
        "where this script runs.\n"
        f"Import error: {e}"
    )


# ---------- Helpers ----------

def normalize_key(s: str) -> str:
    """Normalize metadata keys for robust matching."""
    return s.strip().lower().replace(" ", "_")

def normalize_val(v: Any) -> str:
    """Normalize values for string-based comparison."""
    if v is None:
        return ""
    return str(v).strip().lower()

def coerce_int(val: Any) -> Tuple[bool, int]:
    """Try to coerce a value to int. Returns (ok, value_if_ok_or_0)."""
    try:
        return True, int(str(val).strip())
    except Exception:
        return False, 0

def pick_first_nonempty(*vals: Any) -> Any:
    for v in vals:
        if v not in (None, "", []):
            return v
    return ""

def extract_all(pdf_path: str, password: str = "") -> Dict[str, Any]:
    """Extract everything we need from pdforensic into a single dict."""
    meta = extract_pdf_metadata(pdf_path)  
    # meta is expected to be a dict-like; we normalize keys for lookups
    meta_norm = {normalize_key(k): v for k, v in (meta or {}).items()}

    # Versions / EOFs
    versions_detail = recover_pdf_versions(pdf_path)  
    eof_count = count_pdf_eof_markers(pdf_path)
    no_of_versions = check_no_of_versions(pdf_path)

    # Build a standardized view
    standardized = {
        # Common PD fields (best-effort fallbacks)
        "pdf_version": pick_first_nonempty(meta_norm.get("pdf_version"), meta_norm.get("version"), meta_norm.get("pdfversion")),
        "author": meta_norm.get("author", ""),
        "subject": meta_norm.get("subject", ""),
        "keywords": meta_norm.get("keywords", ""),
        "creator": meta_norm.get("creator", ""),
        "producer": meta_norm.get("producer", ""),
        "creationdate": pick_first_nonempty(meta_norm.get("creationdate"), meta_norm.get("created"), meta_norm.get("creation_date")),
        "moddate": pick_first_nonempty(meta_norm.get("moddate"), meta_norm.get("modified"), meta_norm.get("mod_date")),
        "trapped": meta_norm.get("trapped", ""),
        # Low-level
        "eof_markers": eof_count,
        "pdf_versions": no_of_versions,
        # Raw passthrough for reference
        "_raw_meta": meta,
        "_versions_detail": versions_detail,
    }
    return standardized

def load_brands(brands_json_path: str) -> Dict[str, List[Dict[str, Any]]]:
    with open(brands_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def load_font_data(font_data_json_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load font data templates from statements_font_data.json."""
    with open(font_data_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def best_brand_entry(brand_block: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    If multiple templates exist for a brand, choose the first non-empty
    or the one with the most filled fields. Simple heuristic.
    """
    if not brand_block:
        return {}
    # pick the dict with more non-empty values
    def filled_count(d):
        return sum(1 for k, v in d.items() if v not in (None, "", []))
    brand_block_sorted = sorted(brand_block, key=filled_count, reverse=True)
    return brand_block_sorted[0]

def compare_fields(extracted: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[List[Tuple[str, Any, Any, bool]], float]:
    """
    Compare standardized extracted values against expected template fields.
    Only score non-empty expected fields.
    Returns:
      - list of tuples: (field_name, expected, actual, match_bool)
      - percentage score (0..100)
    """
    # Map some aliases from expected->extracted standardized keys
    key_map = {
        "pdf version": "pdf_version",
        "versions": "pdf_versions",
        "eof_markers": "eof_markers",
        "author": "author",
        "subject": "subject",
        "keywords": "keywords",
        "creator": "creator",
        "producer": "producer",
        "creationdate": "creationdate",
        "moddate": "moddate",
        "trapped": "trapped",
        # allow underscores too
        "pdf_version": "pdf_version",
        "creation_date": "creationdate",
        "mod_date": "moddate",
    }

    results: List[Tuple[str, Any, Any, bool]] = []
    considered = 0
    matched = 0

    for k, v in expected.items():
        if k == "brand":
            # we don't score the brand name here
            continue
        if v in (None, "", []):
            # skip empty expected
            continue
            
        # Skip creationdate and moddate as we'll handle them specially
        k_norm = normalize_key(k)
        if k_norm in ("creationdate", "creation_date", "moddate", "mod_date"):
            continue

        target_key = key_map.get(k_norm, k_norm)
        actual = extracted.get(target_key, "")

        # Numeric comparisons for Versions / eof markers
        if target_key in ("pdf_versions", "eof_markers"):
            ok1, v_int = coerce_int(v)
            ok2, a_int = coerce_int(actual)
            is_match = ok1 and ok2 and (v_int == a_int)
        else:
            # String compare (case-insensitive)
            is_match = normalize_val(v) == normalize_val(actual)

        considered += 1
        matched += 1 if is_match else 0
        results.append((target_key, v, actual, is_match))
    
    # Special check for creation date equals modification date
    creation_date = extracted.get("creationdate", "")
    mod_date = extracted.get("moddate", "")
    dates_equal = normalize_val(creation_date) == normalize_val(mod_date)
    
    # Add this to results with a special field name
    considered += 1
    matched += 1 if dates_equal else 0
    results.append(("dates_equal_check", "True" if dates_equal else "False", 
                   f"creationdate({creation_date}) == moddate({mod_date})", dates_equal))

    pct = (matched / considered * 100.0) if considered else 0.0
    return results, pct

def compare_font_data(extracted_font_data: Dict[str, Any], expected_font_data: Dict[str, Any]) -> Tuple[List[Tuple[str, Any, Any, bool]], float]:
    """
    Compare extracted font data against expected font template.
    Returns:
      - list of tuples: (field_name, expected, actual, match_bool)
      - percentage score (0..100)
    """
    results: List[Tuple[str, Any, Any, bool]] = []
    considered = 0
    matched = 0

    # Compare PDF version
    if expected_font_data.get("pdf_version"):
        expected_version = expected_font_data["pdf_version"]
        actual_version = extracted_font_data.get("pdf_version", "")
        is_match = normalize_val(expected_version) == normalize_val(actual_version)
        considered += 1
        matched += 1 if is_match else 0
        results.append(("font_pdf_version", expected_version, actual_version, is_match))

    # Compare total number of fonts
    if expected_font_data.get("total_no_of_fonts") is not None:
        expected_font_count = expected_font_data["total_no_of_fonts"]
        actual_font_count = extracted_font_data.get("total_no_of_fonts", 0)
        ok1, exp_count = coerce_int(expected_font_count)
        ok2, act_count = coerce_int(actual_font_count)
        is_match = ok1 and ok2 and (exp_count == act_count)
        considered += 1
        matched += 1 if is_match else 0
        results.append(("font_count", expected_font_count, actual_font_count, is_match))

    # Compare font names (if expected font names are provided)
    expected_fonts = expected_font_data.get("font_names", [])
    actual_fonts = extracted_font_data.get("font_names", [])
    
    if expected_fonts:  # Only check if expected fonts are specified
        # Convert to sets for comparison (order doesn't matter)
        expected_font_set = set(normalize_val(f) for f in expected_fonts if f)
        actual_font_set = set(normalize_val(f) for f in actual_fonts if f)
        is_match = expected_font_set == actual_font_set
        considered += 1
        matched += 1 if is_match else 0
        results.append(("font_names", expected_fonts, actual_fonts, is_match))

    # Compare info object (if provided)
    if expected_font_data.get("info_object"):
        expected_info = expected_font_data["info_object"]
        actual_info = extracted_font_data.get("info_object", "")
        is_match = normalize_val(expected_info) == normalize_val(actual_info)
        considered += 1
        matched += 1 if is_match else 0
        results.append(("font_info_object", expected_info, actual_info, is_match))

    pct = (matched / considered * 100.0) if considered else 100.0  # 100% if no font data to check
    return results, pct

def main():
    ap = argparse.ArgumentParser(description="Check PDF brand and compare metadata against statements_metadata.json template.")
    ap.add_argument("pdf", help="Path to the PDF to check")
    ap.add_argument("--brands", default=os.path.join(THIS_DIR, "statements_metadata.json"), help="Path to statements_metadata.json")
    ap.add_argument("--font-data", default=os.path.join(THIS_DIR, "statements_font_data.json"), help="Path to statements_font_data.json")
    ap.add_argument("--password", default="", help="PDF password if any")
    args = ap.parse_args()

    pdf_path = os.path.abspath(args.pdf)
    brands_json_path = os.path.abspath(args.brands)
    font_data_json_path = os.path.abspath(getattr(args, 'font_data', args.font_data))

    if not os.path.exists(pdf_path):
        raise SystemExit(f"PDF not found: {pdf_path}")
    if not os.path.exists(brands_json_path):
        raise SystemExit(f"statements_metadata.json not found: {brands_json_path}")
    if not os.path.exists(font_data_json_path):
        print(f"[!] Font data file not found: {font_data_json_path}. Skipping font comparison.")
        font_data_json_path = None

    # 1) Detect brand
    detected_brand = get_company_name(pdf_path, password=args.password)

    # 2) Extract metadata & internals
    extracted = extract_all(pdf_path)  # Removed password parameter

    # 3) Extract font data
    try:
        extracted_font_data = extract_pdf_font_data(pdf_path)
    except Exception as e:
        print(f"[!] Failed to extract font data: {e}")
        extracted_font_data = {}

    # 4) Load expected templates
    brands = load_brands(brands_json_path)
    brand_key = normalize_val(detected_brand)
    expected_block = brands.get(brand_key, [])

    # Load font data templates if available
    font_results = []
    font_pct = 100.0  # Default to 100% if no font comparison
    if font_data_json_path and extracted_font_data:
        try:
            font_data = load_font_data(font_data_json_path)
            expected_font_block = font_data.get(brand_key, [])
            if expected_font_block:
                expected_font_data = best_brand_entry(expected_font_block)
                font_results, font_pct = compare_font_data(extracted_font_data, expected_font_data)
            else:
                print(f"[!] No font data template found for brand '{detected_brand}'")
        except Exception as e:
            print(f"[!] Error loading or processing font data: {e}")

    # If detection failed, try fallback: pick nothing to compare
    if not expected_block:
        print(f"[!] Brand '{detected_brand}' not found in statements_metadata.json. Metadata scoring skipped.\n")
        print("Extracted summary (for reference):")
        for k in ("pdf_version", "author", "subject", "keywords", "creator", "producer", "creationdate", "moddate", "trapped", "eof_markers", "pdf_versions"):
            print(f"  {k}: {extracted.get(k, '')}")
        
        # Still show font comparison if available
        if font_results:
            print("\nFont Comparison Results:")
            for field, exp, act, ok in font_results:
                status = "✓" if ok else "✗"
                print(f"  [{status}] {field:15s}  expected={exp!r}  actual={act!r}")
            print(f"Font Score: {font_pct:.1f}% match")
        
        sys.exit(2)

    expected = best_brand_entry(expected_block)

    # 5) Compare metadata
    results, pct = compare_fields(extracted, expected)

    # 6) Calculate combined score (metadata + font)
    total_weight = 1.0  # metadata weight
    font_weight = 0.5   # font weight (adjust as needed)
    
    if font_results:
        combined_score = (pct * total_weight + font_pct * font_weight) / (total_weight + font_weight)
    else:
        combined_score = pct

    # 7) Report
    print("=" * 72)
    print(f"PDF: {pdf_path}")
    print(f"Detected brand: {detected_brand}")
    print(f"Template in use: {brand_key}")
    print("-" * 72)
    print("Metadata Comparison (expected vs. actual):")
    for field, exp, act, ok in results:
        status = "✓" if ok else "✗"
        print(f"  [{status}] {field:15s}  expected={exp!r}  actual={act!r}")
    print(f"Metadata Score: {pct:.1f}% match")
    
    if font_results:
        print("-" * 72)
        print("Font Comparison (expected vs. actual):")
        for field, exp, act, ok in font_results:
            status = "✓" if ok else "✗"
            print(f"  [{status}] {field:15s}  expected={exp!r}  actual={act!r}")
        print(f"Font Score: {font_pct:.1f}% match")
        print("-" * 72)
        print(f"Combined Score: {combined_score:.1f}% match (Metadata: {pct:.1f}%, Font: {font_pct:.1f}%)")
    else:
        print("-" * 72)
        print(f"Score: {pct:.1f}% match (Metadata only)")
    print("=" * 72)

    # Optional: exit code thresholding if needed
    # sys.exit(0 if combined_score >= 80 else 1)


def verify_statement_verbose(pdf_path: str, brands_json_path: str = None, font_data_json_path: str = None, password: str = "") -> Dict[str, Any]:
    """
    Perform complete statement verification and return verbose results including font comparison.
    
    Args:
        pdf_path: Path to the PDF file to verify
        brands_json_path: Path to statements_metadata.json file (defaults to package default)
        font_data_json_path: Path to statements_font_data.json file (defaults to package default)
        password: PDF password if required
    
    Returns:
        Dictionary containing:
        - pdf_path: Path to the PDF file
        - detected_brand: Brand detected from PDF
        - template_used: Template key used for comparison
        - verification_score: Percentage score (0-100) for metadata
        - font_score: Percentage score (0-100) for font comparison
        - combined_score: Combined metadata and font score
        - field_results: List of metadata field comparison results
        - font_results: List of font comparison results
        - extracted_metadata: Raw extracted metadata
        - extracted_font_data: Raw extracted font data
        - expected_metadata: Expected metadata template
        - expected_font_data: Expected font data template
        - summary: Human-readable summary
    """
    if brands_json_path is None:
        brands_json_path = os.path.join(THIS_DIR, "statements_metadata.json")
    if font_data_json_path is None:
        font_data_json_path = os.path.join(THIS_DIR, "statements_font_data.json")
    
    pdf_path = os.path.abspath(pdf_path)
    brands_json_path = os.path.abspath(brands_json_path)
    font_data_json_path = os.path.abspath(font_data_json_path)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not os.path.exists(brands_json_path):
        raise FileNotFoundError(f"statements_metadata.json not found: {brands_json_path}")

    # 1) Detect brand
    detected_brand = get_company_name(pdf_path, password=password)

    # 2) Extract metadata & internals
    extracted = extract_all(pdf_path)

    # 3) Extract font data
    extracted_font_data = {}
    try:
        extracted_font_data = extract_pdf_font_data(pdf_path)
    except Exception as e:
        extracted_font_data = {"error": f"Failed to extract font data: {e}"}

    # 4) Load expected templates
    brands = load_brands(brands_json_path)
    brand_key = normalize_val(detected_brand)
    expected_block = brands.get(brand_key, [])

    # Load font data templates
    font_results = []
    font_pct = 100.0  # Default to 100% if no font comparison
    expected_font_data = {}
    
    if os.path.exists(font_data_json_path) and not extracted_font_data.get("error"):
        try:
            font_data = load_font_data(font_data_json_path)
            expected_font_block = font_data.get(brand_key, [])
            if expected_font_block:
                expected_font_data = best_brand_entry(expected_font_block)
                font_results, font_pct = compare_font_data(extracted_font_data, expected_font_data)
        except Exception as e:
            font_results = [("font_comparison_error", "", f"Error: {e}", False)]
            font_pct = 0.0

    # If detection failed, return error info
    if not expected_block:
        return {
            "pdf_path": pdf_path,
            "detected_brand": detected_brand,
            "template_used": None,
            "verification_score": 0.0,
            "font_score": font_pct,
            "combined_score": font_pct * 0.5,  # Only font score with reduced weight
            "field_results": [],
            "font_results": font_results,
            "extracted_metadata": extracted,
            "extracted_font_data": extracted_font_data,
            "expected_metadata": {},
            "expected_font_data": expected_font_data,
            "summary": f"Brand '{detected_brand}' not found in statements_metadata.json. No metadata template available for comparison.",
            "error": f"Brand '{detected_brand}' not found in templates"
        }

    expected = best_brand_entry(expected_block)

    # 5) Compare metadata
    results, pct = compare_fields(extracted, expected)

    # 6) Calculate combined score
    total_weight = 1.0  # metadata weight
    font_weight = 0.5   # font weight
    
    if font_results:
        combined_score = (pct * total_weight + font_pct * font_weight) / (total_weight + font_weight)
    else:
        combined_score = pct

    # 7) Build field results with detailed info
    field_results = []
    for field, exp, act, ok in results:
        field_results.append({
            "field": field,
            "expected": exp,
            "actual": act,
            "match": ok,
            "status": "✓" if ok else "✗"
        })

    # 8) Build font results with detailed info
    font_field_results = []
    for field, exp, act, ok in font_results:
        font_field_results.append({
            "field": field,
            "expected": exp,
            "actual": act,
            "match": ok,
            "status": "✓" if ok else "✗"
        })

    # 9) Create summary
    total_fields = len(field_results)
    matched_fields = sum(1 for r in field_results if r["match"])
    total_font_fields = len(font_field_results)
    matched_font_fields = sum(1 for r in font_field_results if r["match"])
    
    summary_lines = [
        f"PDF: {os.path.basename(pdf_path)}",
        f"Detected brand: {detected_brand}",
        f"Template used: {brand_key}",
        f"Metadata fields checked: {total_fields}",
        f"Metadata fields matched: {matched_fields}",
        f"Metadata score: {pct:.1f}%",
        f"Font fields checked: {total_font_fields}",
        f"Font fields matched: {matched_font_fields}",
        f"Font score: {font_pct:.1f}%",
        f"Combined verification score: {combined_score:.1f}%"
    ]
    
    return {
        "pdf_path": pdf_path,
        "detected_brand": detected_brand,
        "template_used": brand_key,
        "verification_score": pct,
        "font_score": font_pct,
        "combined_score": combined_score,
        "field_results": field_results,
        "font_results": font_field_results,
        "extracted_metadata": extracted,
        "extracted_font_data": extracted_font_data,
        "expected_metadata": expected,
        "expected_font_data": expected_font_data,
        "summary": "\n".join(summary_lines),
        "total_fields": total_fields,
        "matched_fields": matched_fields,
        "total_font_fields": total_font_fields,
        "matched_font_fields": matched_font_fields
    }


def print_verification_report(verification_result: Dict[str, Any]) -> None:
    """
    Print a formatted verification report from verification results.
    
    Args:
        verification_result: Result from verify_statement_verbose()
    """
    result = verification_result
    
    print("=" * 72)
    print(result["summary"])
    print("-" * 72)
    print("Metadata Comparison (expected vs. actual):")
    
    for field_result in result["field_results"]:
        status = field_result["status"]
        field = field_result["field"]
        exp = field_result["expected"]
        act = field_result["actual"]
        print(f"  [{status}] {field:15s}  expected={exp!r}  actual={act!r}")
    
    if result.get("font_results"):
        print("-" * 72)
        print("Font Comparison (expected vs. actual):")
        
        for font_result in result["font_results"]:
            status = font_result["status"]
            field = font_result["field"]
            exp = font_result["expected"]
            act = font_result["actual"]
            print(f"  [{status}] {field:15s}  expected={exp!r}  actual={act!r}")
    
    print("-" * 72)
    if result.get("font_results"):
        print(f"Metadata Score: {result['verification_score']:.1f}% | Font Score: {result['font_score']:.1f}% | Combined: {result['combined_score']:.1f}%")
    else:
        print(f"Score: {result['verification_score']:.1f}% match (Metadata only)")
    print("=" * 72)


if __name__ == "__main__":
    main()
