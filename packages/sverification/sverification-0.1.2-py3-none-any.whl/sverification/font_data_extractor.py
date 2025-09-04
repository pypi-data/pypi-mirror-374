from pdf_font_checker import get_pdf_info_dict


def extract_pdf_font_data(pdf_path):
    """
    Extract font data from a PDF file using pdf_font_checker.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing PDF font information with keys:
            - pdf_version: Version of the PDF
            - total_no_of_fonts: Total number of fonts in the PDF
            - font_names: List of font names used in the PDF
            - info_object: PDF info object reference
            
    Example:
        >>> result = extract_pdf_font_data("document.pdf")
        >>> print(result)
        {'pdf_version': 'PDF-1.4', 'total_no_of_fonts': 2, 'font_names': ['Helvetica', 'AZHGJL+ArialMT'], 'info_object': '20 0 R'}
    """
    return get_pdf_info_dict(pdf_path)

