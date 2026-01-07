#!/usr/bin/env python3
"""
Markdown to HTML converter for financial research reports
Properly converts markdown sections to HTML while preserving structure and formatting
"""

import re
from typing import Tuple
from pathlib import Path


def convert_markdown_to_html(markdown_text: str) -> Tuple[str, str]:
    """
    Convert markdown to HTML in two parts: content and bibliography

    Args:
        markdown_text: Full markdown report text

    Returns:
        Tuple of (content_html, bibliography_html)
    """
    # Split content and bibliography
    parts = markdown_text.split('## Bibliography')
    content_md = parts[0]
    bibliography_md = parts[1] if len(parts) > 1 else ""

    # Convert content (everything except bibliography)
    content_html = _convert_content_section(content_md)

    # Convert bibliography separately
    bibliography_html = _convert_bibliography_section(bibliography_md)

    return content_html, bibliography_html


def _convert_content_section(markdown: str) -> str:
    """Convert main content sections to HTML"""
    html = markdown

    # Remove title and front matter
    lines = html.split('\n')
    processed_lines = []
    skip_until_first_section = True

    for line in lines:
        if skip_until_first_section:
            if line.startswith('## ') and not line.startswith('### '):
                skip_until_first_section = False
                processed_lines.append(line)
            continue
        processed_lines.append(line)

    html = '\n'.join(processed_lines)

    # Convert headers
    html = re.sub(
        r'^## (.+)$',
        r'<div class="section"><h2 class="section-title">\1</h2>',
        html,
        flags=re.MULTILINE
    )

    html = re.sub(
        r'^### (.+)$',
        r'<h3 class="subsection-title">\1</h3>',
        html,
        flags=re.MULTILINE
    )

    html = re.sub(
        r'^#### (.+)$',
        r'<h4 class="subsubsection-title">\1</h4>',
        html,
        flags=re.MULTILINE
    )

    # Convert **bold** text
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Convert *italic* text
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Convert inline code
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # Convert lists
    html = _convert_lists(html)

    # Convert tables
    html = _convert_tables(html)

    # Convert paragraphs
    html = _convert_paragraphs(html)

    # Close sections
    html = _close_sections(html)

    # Wrap executive summary
    html = html.replace(
        '<h2 class="section-title">Executive Summary</h2>',
        '<div class="executive-summary"><h2 class="section-title">Executive Summary</h2>'
    )
    if '<div class="executive-summary">' in html:
        html = html.replace(
            '</h2>\n<div class="section">',
            '</h2></div>\n<div class="section">',
            1
        )

    return html


def _convert_bibliography_section(markdown: str) -> str:
    """Convert bibliography section to HTML with tier organization"""
    if not markdown.strip():
        return ""

    html = markdown

    # Convert tier headers
    html = re.sub(
        r'^### (Tier \d.+)$',
        r'<div class="bib-tier"><div class="bib-tier-title">\1</div>',
        html,
        flags=re.MULTILINE
    )

    # Convert citation entries
    html = re.sub(
        r'\[(\d+)\]\s*(.+?)\s*(https?://[^\s\)]+)',
        r'<div class="bib-entry"><span class="bib-number">[\1]</span> \2 <a href="\3" target="_blank">\3</a></div>',
        html
    )

    # Convert bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    html = f'<div class="bibliography-content">{html}</div>'

    return html


def _convert_lists(html: str) -> str:
    """Convert markdown lists to HTML lists"""
    lines = html.split('\n')
    result = []
    in_list = False
    list_type = None

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result.append('<ul>')
                in_list = True
                list_type = 'ul'
            content = stripped[2:]
            result.append(f'<li>{content}</li>')

        elif re.match(r'^\d+\.\s', stripped):
            if not in_list:
                result.append('<ol>')
                in_list = True
                list_type = 'ol'
            content = re.sub(r'^\d+\.\s', '', stripped)
            result.append(f'<li>{content}</li>')

        else:
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
                list_type = None
            result.append(line)

    if in_list:
        result.append(f'</{list_type}>')

    return '\n'.join(result)


def _convert_tables(html: str) -> str:
    """Convert markdown tables to HTML tables"""
    lines = html.split('\n')
    result = []
    in_table = False
    is_header = False

    for line in lines:
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                result.append('<table class="data-table">')
                in_table = True
                is_header = True
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                result.append('<thead><tr>')
                for cell in cells:
                    result.append(f'<th>{cell}</th>')
                result.append('</tr></thead>')
                result.append('<tbody>')
            elif '---' in line:
                continue
            else:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                result.append('<tr>')
                for cell in cells:
                    # Add numeric class for numbers
                    css_class = 'numeric' if re.match(r'^[\$\d\.\,\%\+\-]+$', cell.replace('B', '').replace('M', '').replace('K', '')) else ''
                    # Add positive/negative class for changes
                    if cell.startswith('+'):
                        css_class += ' positive'
                    elif cell.startswith('-') and '%' in cell:
                        css_class += ' negative'
                    result.append(f'<td class="{css_class.strip()}">{cell}</td>')
                result.append('</tr>')
        else:
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            result.append(line)

    if in_table:
        result.append('</tbody></table>')

    return '\n'.join(result)


def _convert_paragraphs(html: str) -> str:
    """Wrap non-HTML lines in paragraph tags"""
    lines = html.split('\n')
    result = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
            continue

        if (stripped.startswith('<') and stripped.endswith('>')) or \
           stripped.startswith('</') or \
           '<h' in stripped or '<div' in stripped or '<ul' in stripped or \
           '<ol' in stripped or '<li' in stripped or '<table' in stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
            continue

        if not in_paragraph:
            result.append('<p>' + line)
            in_paragraph = True
        else:
            result.append(line)

    if in_paragraph:
        result.append('</p>')

    return '\n'.join(result)


def _close_sections(html: str) -> str:
    """Close all open section divs"""
    lines = html.split('\n')
    result = []
    section_open = False

    for line in lines:
        if '<div class="section">' in line:
            if section_open:
                result.append('</div>')
            section_open = True
        result.append(line)

    if section_open:
        result.append('</div>')

    return '\n'.join(result)


def main():
    """Test the converter"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python md_to_html.py <markdown_file>")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    if not md_file.exists():
        print(f"Error: File {md_file} not found")
        sys.exit(1)

    markdown_text = md_file.read_text()
    content_html, bib_html = convert_markdown_to_html(markdown_text)

    print("=== CONTENT HTML ===")
    print(content_html[:1500])
    print("\n=== BIBLIOGRAPHY HTML ===")
    print(bib_html[:500])


if __name__ == "__main__":
    main()
