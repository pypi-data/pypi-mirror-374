"""
HTML to PDF converter using multiple rendering engines.
"""

import sys
import os
import tempfile
from typing import Optional

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.ast import ASTNode, NodeType
from core.exceptions import ConversionError, DependencyError

class Html2PdfConverter:
    """Converts HTML files to PDF format using various rendering engines."""
    
    def __init__(self):
        self.available_engines = self._check_available_engines()
        
    def _check_available_engines(self) -> dict:
        """Check which rendering engines are available."""
        engines = {}
        
        # Check for WeasyPrint
        try:
            import weasyprint
            engines['weasyprint'] = weasyprint
        except ImportError:
            pass
        
        # Check for pdfkit (wkhtmltopdf)
        try:
            import pdfkit
            engines['pdfkit'] = pdfkit
        except ImportError:
            pass
        
        # Check for Playwright
        try:
            from playwright.sync_api import sync_playwright
            engines['playwright'] = sync_playwright
        except ImportError:
            pass
        
        # Check for Selenium
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            engines['selenium'] = webdriver
        except ImportError:
            pass
            
        return engines
    
    def parse_html2ast(self, input_path: str) -> ASTNode:
        """Parse HTML to AST representation."""
        # Reuse the HTML parser from html2md converter
        from .html2md import Html2MdConverter
        html_converter = Html2MdConverter()
        return html_converter.parse_html2ast(input_path)
    
    def ast2pdf(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to PDF via HTML intermediate."""
        # Convert AST to HTML first, then to PDF
        temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        try:
            from core.mapper import ast2html
            ast2html(ast_root, temp_html.name)
            self._convert_html_to_pdf(temp_html.name, output_path)
        finally:
            os.unlink(temp_html.name)
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert HTML to PDF using the best available method."""
        
        if not self.available_engines:
            raise DependencyError(
                "No HTML to PDF rendering engine available. Install one of: weasyprint, pdfkit, playwright, or selenium",
                suggestions=[
                    "pip install weasyprint (recommended)",
                    "pip install pdfkit && install wkhtmltopdf system package",
                    "pip install playwright && playwright install chromium",
                    "pip install selenium && install ChromeDriver"
                ]
            )
        
        # Try engines in order of preference
        engine_order = ['weasyprint', 'pdfkit', 'playwright', 'selenium']
        
        for engine_name in engine_order:
            if engine_name in self.available_engines:
                try:
                    if engine_name == 'weasyprint':
                        self._convert_with_weasyprint(input_path, output_path)
                    elif engine_name == 'pdfkit':
                        self._convert_with_pdfkit(input_path, output_path)
                    elif engine_name == 'playwright':
                        self._convert_with_playwright(input_path, output_path)
                    elif engine_name == 'selenium':
                        self._convert_with_selenium(input_path, output_path)
                    
                    print(f"Successfully converted '{input_path}' to '{output_path}' using {engine_name}")
                    return
                    
                except Exception as e:
                    print(f"Warning: {engine_name} conversion failed: {e}")
                    continue
        
        raise ConversionError(
            "All HTML to PDF conversion methods failed",
            suggestions=["Check that the HTML file is valid", "Try installing a different rendering engine"]
        )
    
    def _convert_html_to_pdf(self, html_path: str, output_path: str) -> None:
        """Convert HTML file to PDF using available engine."""
        self.convert(html_path, output_path)
    
    def _convert_with_weasyprint(self, input_path: str, output_path: str) -> None:
        """Convert using WeasyPrint (best quality, CSS support)."""
        weasyprint = self.available_engines['weasyprint']
        
        # Read HTML content
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Create PDF
        html_doc = weasyprint.HTML(string=html_content, base_url=os.path.dirname(input_path))
        html_doc.write_pdf(output_path)
    
    def _convert_with_pdfkit(self, input_path: str, output_path: str) -> None:
        """Convert using pdfkit (wkhtmltopdf wrapper)."""
        pdfkit = self.available_engines['pdfkit']
        
        options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        try:
            pdfkit.from_file(input_path, output_path, options=options)
        except OSError as e:
            if "wkhtmltopdf" in str(e):
                raise DependencyError(
                    "wkhtmltopdf system package is required for pdfkit",
                    suggestions=[
                        "Install wkhtmltopdf: apt-get install wkhtmltopdf (Ubuntu/Debian)",
                        "Install wkhtmltopdf: brew install wkhtmltopdf (macOS)",
                        "Download from: https://wkhtmltopdf.org/downloads.html"
                    ]
                ) from e
            raise
    
    def _convert_with_playwright(self, input_path: str, output_path: str) -> None:
        """Convert using Playwright browser automation."""
        sync_playwright = self.available_engines['playwright']
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Load HTML file
                file_url = f"file://{os.path.abspath(input_path)}"
                page.goto(file_url)
                
                # Generate PDF
                page.pdf(path=output_path, format='A4', print_background=True)
                
            except Exception as e:
                if "chromium" in str(e).lower():
                    raise DependencyError(
                        "Chromium browser not found for Playwright",
                        suggestions=["Run: playwright install chromium"]
                    ) from e
                raise
            finally:
                browser.close()
    
    def _convert_with_selenium(self, input_path: str, output_path: str) -> None:
        """Convert using Selenium Chrome WebDriver."""
        webdriver = self.available_engines['selenium']
        
        try:
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError as e:
            raise DependencyError(
                "webdriver-manager is required for Selenium",
                missing_dependency="webdriver-manager"
            ) from e
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            # Auto-install ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Load HTML file
                file_url = f"file://{os.path.abspath(input_path)}"
                driver.get(file_url)
                
                # Execute Chrome DevTools command to save as PDF
                result = driver.execute_cdp_cmd("Page.printToPDF", {
                    "format": "A4",
                    "printBackground": True,
                    "marginTop": 0.4,
                    "marginBottom": 0.4,
                    "marginLeft": 0.4,
                    "marginRight": 0.4
                })
                
                # Save PDF data
                import base64
                pdf_data = base64.b64decode(result['data'])
                
                with open(output_path, 'wb') as f:
                    f.write(pdf_data)
                    
            finally:
                driver.quit()
                
        except Exception as e:
            if "chromedriver" in str(e).lower() or "chrome" in str(e).lower():
                raise DependencyError(
                    "ChromeDriver or Chrome browser not found",
                    suggestions=[
                        "Install Chrome browser",
                        "pip install webdriver-manager to auto-install ChromeDriver"
                    ]
                ) from e
            raise