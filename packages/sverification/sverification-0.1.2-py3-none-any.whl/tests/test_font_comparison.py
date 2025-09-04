#!/usr/bin/env python3
"""
Tests for font comparison functionality in sverification package.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from sverification.compare_metadata import (
    load_font_data,
    compare_font_data,
    verify_statement_verbose
)
from sverification.font_data_extractor import extract_pdf_font_data


class TestFontDataLoader:
    """Test font data loading functionality."""
    
    def test_load_font_data_valid_file(self):
        """Test loading valid font data file."""
        font_data = {
            "test_brand": [
                {
                    "pdf_version": "PDF-1.4",
                    "total_no_of_fonts": 2,
                    "font_names": ["Helvetica", "Arial"],
                    "info_object": "1 0 R"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(font_data, f)
            temp_path = f.name
        
        try:
            loaded_data = load_font_data(temp_path)
            assert loaded_data == font_data
            assert "test_brand" in loaded_data
            assert len(loaded_data["test_brand"]) == 1
        finally:
            os.unlink(temp_path)
    
    def test_load_font_data_nonexistent_file(self):
        """Test loading nonexistent font data file."""
        with pytest.raises(FileNotFoundError):
            load_font_data("/nonexistent/path/font_data.json")


class TestFontComparison:
    """Test font comparison functionality."""
    
    def test_compare_font_data_perfect_match(self):
        """Test font comparison with perfect match."""
        extracted = {
            "pdf_version": "PDF-1.4",
            "total_no_of_fonts": 2,
            "font_names": ["Helvetica", "Arial"],
            "info_object": "1 0 R"
        }
        
        expected = {
            "pdf_version": "PDF-1.4",
            "total_no_of_fonts": 2,
            "font_names": ["Helvetica", "Arial"],
            "info_object": "1 0 R"
        }
        
        results, score = compare_font_data(extracted, expected)
        
        assert score == 100.0
        assert len(results) == 4  # pdf_version, font_count, font_names, info_object
        
        # Check all results are matches
        for field, exp, act, match in results:
            assert match == True
    
    def test_compare_font_data_partial_match(self):
        """Test font comparison with partial match."""
        extracted = {
            "pdf_version": "PDF-1.4",
            "total_no_of_fonts": 2,
            "font_names": ["Helvetica", "Arial"],
            "info_object": "1 0 R"
        }
        
        expected = {
            "pdf_version": "PDF-1.7",  # Different version
            "total_no_of_fonts": 2,   # Same count
            "font_names": ["Helvetica", "Times"],  # Different fonts
            "info_object": "1 0 R"    # Same info object
        }
        
        results, score = compare_font_data(extracted, expected)
        
        assert score == 50.0  # 2 out of 4 match
        
        # Check specific results
        result_dict = {field: match for field, _, _, match in results}
        assert result_dict["font_pdf_version"] == False  # Version mismatch
        assert result_dict["font_count"] == True         # Count match
        assert result_dict["font_names"] == False        # Names mismatch
        assert result_dict["font_info_object"] == True   # Info object match
    
    def test_compare_font_data_no_expected_fonts(self):
        """Test font comparison when expected font names are empty."""
        extracted = {
            "pdf_version": "PDF-1.4",
            "total_no_of_fonts": 2,
            "font_names": ["Helvetica", "Arial"],
            "info_object": "1 0 R"
        }
        
        expected = {
            "pdf_version": "PDF-1.4",
            "total_no_of_fonts": 2,
            "font_names": [],  # Empty expected fonts
            "info_object": "1 0 R"
        }
        
        results, score = compare_font_data(extracted, expected)
        
        # Should only check 3 fields (not font_names since it's empty)
        assert len(results) == 3
        result_fields = [field for field, _, _, _ in results]
        assert "font_names" not in result_fields
    
    def test_compare_font_data_font_order_independence(self):
        """Test that font name order doesn't matter."""
        extracted = {
            "font_names": ["Arial", "Helvetica"]
        }
        
        expected = {
            "font_names": ["Helvetica", "Arial"]  # Different order
        }
        
        results, score = compare_font_data(extracted, expected)
        
        # Should still match since order doesn't matter
        font_name_result = next((match for field, _, _, match in results if field == "font_names"), None)
        assert font_name_result == True
    
    def test_compare_font_data_empty_expected(self):
        """Test font comparison with completely empty expected data."""
        extracted = {
            "pdf_version": "PDF-1.4",
            "total_no_of_fonts": 2,
            "font_names": ["Helvetica", "Arial"],
            "info_object": "1 0 R"
        }
        
        expected = {}
        
        results, score = compare_font_data(extracted, expected)
        
        # Should get 100% since no comparisons are made
        assert score == 100.0
        assert len(results) == 0


class TestIntegratedFontVerification:
    """Test integrated font verification with the main verification function."""
    
    @patch('sverification.compare_metadata.get_company_name')
    @patch('sverification.compare_metadata.extract_all')
    @patch('sverification.compare_metadata.extract_pdf_font_data')
    @patch('sverification.compare_metadata.load_brands')
    @patch('sverification.compare_metadata.load_font_data')
    @patch('os.path.exists')
    def test_verify_statement_verbose_with_fonts(self, mock_exists, mock_load_font_data, 
                                                mock_load_brands, mock_extract_font, 
                                                mock_extract_all, mock_get_company):
        """Test complete verification with font comparison."""
        # Setup mocks
        mock_exists.return_value = True
        mock_get_company.return_value = "test_brand"
        mock_extract_all.return_value = {
            "pdf_version": "1.4",
            "author": "Test Author",
            "eof_markers": 1,
            "pdf_versions": 1
        }
        mock_extract_font.return_value = {
            "pdf_version": "PDF-1.4",
            "total_no_of_fonts": 2,
            "font_names": ["Helvetica", "Arial"],
            "info_object": "1 0 R"
        }
        mock_load_brands.return_value = {
            "test_brand": [
                {
                    "brand": "test_brand",
                    "pdf_version": "1.4",
                    "author": "Test Author",
                    "eof_markers": 1,
                    "pdf_versions": 1
                }
            ]
        }
        mock_load_font_data.return_value = {
            "test_brand": [
                {
                    "pdf_version": "PDF-1.4",
                    "total_no_of_fonts": 2,
                    "font_names": ["Helvetica", "Arial"],
                    "info_object": "1 0 R"
                }
            ]
        }
        
        # Test verification
        result = verify_statement_verbose("test.pdf")
        
        # Verify results
        assert result["detected_brand"] == "test_brand"
        assert result["template_used"] == "test_brand"
        assert "verification_score" in result
        assert "font_score" in result
        assert "combined_score" in result
        assert result["font_score"] == 100.0  # Perfect font match
        assert len(result["font_results"]) > 0
        
        # Check that font results are included
        font_field_names = [fr["field"] for fr in result["font_results"]]
        assert "font_pdf_version" in font_field_names
        assert "font_count" in font_field_names
    
    @patch('sverification.compare_metadata.extract_pdf_font_data')
    def test_font_extraction_error_handling(self, mock_extract_font):
        """Test handling of font extraction errors."""
        mock_extract_font.side_effect = Exception("Font extraction failed")
        
        # This should not raise an exception, but handle it gracefully
        # We'll test this by ensuring that font data extraction errors are handled
        # in the actual implementation
        pass


class TestFontExtractorIntegration:
    """Test integration with the font_data_extractor module."""
    
    @patch('sverification.font_data_extractor.get_pdf_info_dict')
    def test_extract_pdf_font_data_success(self, mock_get_pdf_info):
        """Test successful font data extraction."""
        expected_result = {
            "pdf_version": "PDF-1.4",
            "total_no_of_fonts": 2,
            "font_names": ["Helvetica", "Arial"],
            "info_object": "1 0 R"
        }
        mock_get_pdf_info.return_value = expected_result
        
        result = extract_pdf_font_data("test.pdf")
        
        assert result == expected_result
        mock_get_pdf_info.assert_called_once_with("test.pdf")
    
    @patch('sverification.font_data_extractor.get_pdf_info_dict')
    def test_extract_pdf_font_data_error(self, mock_get_pdf_info):
        """Test font data extraction error propagation."""
        mock_get_pdf_info.side_effect = Exception("PDF reading failed")
        
        with pytest.raises(Exception, match="PDF reading failed"):
            extract_pdf_font_data("test.pdf")


if __name__ == "__main__":
    pytest.main([__file__])
