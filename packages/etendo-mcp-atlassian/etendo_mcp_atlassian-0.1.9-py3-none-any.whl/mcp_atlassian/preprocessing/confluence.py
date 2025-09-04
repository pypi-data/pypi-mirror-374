"""Confluence-specific text preprocessing module."""

import logging
import shutil
import tempfile
from pathlib import Path

# Try to import md2cf first, then fallback to md2conf, then to a basic implementation
MD_CONVERTER_AVAILABLE = False
try:
    # nombre más común en PyPI
    from md2cf.converter import (
        ConfluenceConverterOptions,
        ConfluenceStorageFormatConverter,
        elements_from_string,
        elements_to_string,
        markdown_to_html,
    )
    MD_CONVERTER_AVAILABLE = True
except ModuleNotFoundError:
    try:
        # fallback si alguien instala otro fork con ese nombre
        from md2conf.converter import (
            ConfluenceConverterOptions,
            ConfluenceStorageFormatConverter,
            elements_from_string,
            elements_to_string,
            markdown_to_html,
        )
        MD_CONVERTER_AVAILABLE = True
    except ModuleNotFoundError:
        # Fallback básico - el warning se mostrará más tarde cuando se use
        MD_CONVERTER_AVAILABLE = False

# Basic markdown to HTML converter if md2cf is not available
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ModuleNotFoundError:
    try:
        from markdownify import markdownify
        MARKDOWN_AVAILABLE = True
    except ModuleNotFoundError:
        MARKDOWN_AVAILABLE = False

from .base import BasePreprocessor

logger = logging.getLogger("mcp-atlassian")


class ConfluencePreprocessor(BasePreprocessor):
    """Handles text preprocessing for Confluence content."""

    def __init__(self, base_url: str) -> None:
        """
        Initialize the Confluence text preprocessor.

        Args:
            base_url: Base URL for Confluence API
        """
        super().__init__(base_url=base_url)

    def markdown_to_confluence_storage(
        self, markdown_content: str, *, enable_heading_anchors: bool = False
    ) -> str:
        """
        Convert Markdown content to Confluence storage format (XHTML)

        Args:
            markdown_content: Markdown text to convert
            enable_heading_anchors: Whether to enable automatic heading anchor generation (default: False)

        Returns:
            Confluence storage format (XHTML) string
        """
        if not MD_CONVERTER_AVAILABLE:
            logger.warning("md2cf/md2conf not available, using basic markdown conversion")
            return self._basic_markdown_to_confluence(markdown_content)
            
        try:
            # First convert markdown to HTML
            html_content = markdown_to_html(markdown_content)

            # Create a temporary directory for any potential attachments
            temp_dir = tempfile.mkdtemp()

            try:
                # Parse the HTML into an element tree
                root = elements_from_string(html_content)

                # Create converter options
                options = ConfluenceConverterOptions(
                    ignore_invalid_url=True,
                    heading_anchors=enable_heading_anchors,
                    render_mermaid=False,
                )

                # Create a converter
                converter = ConfluenceStorageFormatConverter(
                    options=options,
                    path=Path(temp_dir) / "temp.md",
                    root_dir=Path(temp_dir),
                    page_metadata={},
                )

                # Transform the HTML to Confluence storage format
                converter.visit(root)

                # Convert the element tree back to a string
                storage_format = elements_to_string(root)

                return str(storage_format)
            finally:
                # Clean up the temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            logger.error(f"Error converting markdown to Confluence storage format: {e}")
            logger.exception(e)

            # Fall back to basic conversion
            return self._basic_markdown_to_confluence(markdown_content)

    def _basic_markdown_to_confluence(self, markdown_content: str) -> str:
        """
        Basic fallback for markdown to Confluence conversion when md2cf is not available
        
        Args:
            markdown_content: Markdown text to convert
            
        Returns:
            Basic Confluence storage format string
        """
        try:
            if MARKDOWN_AVAILABLE:
                try:
                    import markdown
                    # Use markdown library to convert to HTML
                    html_content = markdown.markdown(markdown_content)
                except ImportError:
                    # Very basic conversion
                    html_content = self._simple_markdown_to_html(markdown_content)
            else:
                html_content = self._simple_markdown_to_html(markdown_content)
            
            # Wrap in basic Confluence storage format
            storage_format = f"""<ac:rich-text-body>{html_content}</ac:rich-text-body>"""
            return storage_format
            
        except Exception as e:
            logger.error(f"Error in basic markdown conversion: {e}")
            # Last resort: just wrap the markdown as preformatted text
            return f"""<ac:rich-text-body><pre>{markdown_content}</pre></ac:rich-text-body>"""
    
    def _simple_markdown_to_html(self, markdown_content: str) -> str:
        """
        Very basic markdown to HTML conversion for when no markdown library is available
        """
        import re
        
        html = markdown_content
        
        # Headers
        html = re.sub(r'^### (.*)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'
        
        return html

    # Confluence-specific methods can be added here
