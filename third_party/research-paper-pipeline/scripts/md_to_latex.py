#!/usr/bin/env python3
"""
Markdown to LaTeX converter for academic papers.
Converts a Markdown paper draft into LaTeX using a specified conference template.

Usage:
    python md_to_latex.py input.md output.tex --venue neurips_2026 --bib references.bib
"""

import argparse
import re
import sys
from pathlib import Path

VENUE_CONFIGS = {
    "neurips_2026": {
        "documentclass": r"\documentclass{article}",
        "packages": [
            r"\usepackage[final]{neurips_2026}",
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage{hyperref}",
            r"\usepackage{url}",
            r"\usepackage{booktabs}",
            r"\usepackage{amsfonts}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
            r"\usepackage{nicefrac}",
            r"\usepackage{microtype}",
            r"\usepackage{xcolor}",
            r"\usepackage{graphicx}",
            r"\usepackage{algorithm}",
            r"\usepackage{algorithmic}",
            r"\usepackage{natbib}",
        ],
        "bibstyle": "plainnat",
        "columns": "single",
    },
    "icml_2026": {
        "documentclass": r"\documentclass[accepted]{icml2026}",
        "packages": [
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{algorithm}",
            r"\usepackage{algorithmic}",
            r"\usepackage{natbib}",
            r"\usepackage{hyperref}",
        ],
        "bibstyle": "icml2026",
        "columns": "double",
    },
    "iclr_2026": {
        "documentclass": r"\documentclass{article}",
        "packages": [
            r"\usepackage{iclr2026_conference}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{algorithm}",
            r"\usepackage{algorithmic}",
            r"\usepackage{natbib}",
            r"\usepackage{hyperref}",
        ],
        "bibstyle": "iclr2026_conference",
        "columns": "single",
    },
    "cvpr_2026": {
        "documentclass": r"\documentclass[10pt,twocolumn,letterpaper]{article}",
        "packages": [
            r"\usepackage{cvpr}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{algorithm}",
            r"\usepackage{algorithmic}",
            r"\usepackage{hyperref}",
        ],
        "bibstyle": "ieee_fullname",
        "columns": "double",
    },
    "acl_2026": {
        "documentclass": r"\documentclass[11pt]{article}",
        "packages": [
            r"\usepackage{acl}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{algorithm}",
            r"\usepackage{algorithmic}",
            r"\usepackage{natbib}",
            r"\usepackage{hyperref}",
        ],
        "bibstyle": "acl_natbib",
        "columns": "double",
    },
    "iccse_2026": {
        "documentclass": r"\documentclass[conference]{IEEEtran}",
        "packages": [
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{algorithm}",
            r"\usepackage{algorithmic}",
            r"\usepackage{hyperref}",
            r"\usepackage{url}",
            r"\usepackage{cite}",
            r"\usepackage{xcolor}",
        ],
        "bibstyle": "IEEEtran",
        "columns": "double",
    },
}


def convert_citations(text: str, use_natbib: bool = True) -> str:
    """Convert Markdown citations to LaTeX.

    Args:
        use_natbib: If True, uses \\citep/\\citet (natbib). If False, uses \\cite (IEEE style).
    """
    if use_natbib:
        def multi_cite(m):
            keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
            return r"\citep{" + ", ".join(keys) + "}"

        text = re.sub(r"\[(@[^]]+)\]", multi_cite, text)
        text = re.sub(r"(?<!\[)@(\w+)(?!\])", r"\\citet{\1}", text)
    else:
        def multi_cite(m):
            keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
            return r"\cite{" + ", ".join(keys) + "}"

        text = re.sub(r"\[(@[^]]+)\]", multi_cite, text)
        text = re.sub(r"(?<!\[)@(\w+)(?!\])", r"\\cite{\1}", text)

    return text


def convert_headings(text: str) -> str:
    """Convert Markdown headings to LaTeX sections."""
    lines = text.split("\n")
    result = []
    title = None

    for line in lines:
        if line.startswith("# ") and title is None:
            title = line[2:].strip()
            continue
        elif line.startswith("#### "):
            heading = line[5:].strip()
            result.append(f"\\paragraph{{{heading}}}")
        elif line.startswith("### "):
            heading = line[4:].strip()
            result.append(f"\\subsubsection{{{heading}}}")
        elif line.startswith("## "):
            heading = line[3:].strip()
            # Strip numbering like "1. " or "4.2 "
            heading = re.sub(r"^\d+(\.\d+)*\.?\s*", "", heading)
            result.append(f"\\section{{{heading}}}")
        else:
            result.append(line)

    return title, "\n".join(result)


def convert_bold_italic(text: str) -> str:
    """Convert Markdown bold/italic to LaTeX."""
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"\\textbf{\\textit{\1}}", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"\*(.+?)\*", r"\\textit{\1}", text)
    return text


def convert_tables(text: str) -> str:
    """Convert Markdown tables to LaTeX tabular."""
    lines = text.split("\n")
    result = []
    i = 0

    while i < len(lines):
        if "|" in lines[i] and i + 1 < len(lines) and re.match(r"^\s*\|[\s\-:|]+\|\s*$", lines[i + 1]):
            table_lines = []
            j = i
            while j < len(lines) and "|" in lines[j]:
                table_lines.append(lines[j])
                j += 1

            header = [c.strip() for c in table_lines[0].split("|")[1:-1]]
            ncols = len(header)
            col_spec = "l" + "c" * (ncols - 1)

            latex_table = []
            latex_table.append("\\begin{table}[t]")
            latex_table.append("\\centering")
            latex_table.append(f"\\begin{{tabular}}{{{col_spec}}}")
            latex_table.append("\\toprule")
            latex_table.append(" & ".join(header) + " \\\\")
            latex_table.append("\\midrule")

            for row_line in table_lines[2:]:
                cells = [c.strip() for c in row_line.split("|")[1:-1]]
                cells = [c.replace("**", "") for c in cells]
                latex_table.append(" & ".join(cells) + " \\\\")

            latex_table.append("\\bottomrule")
            latex_table.append("\\end{tabular}")
            latex_table.append("\\end{table}")

            result.append("\n".join(latex_table))
            i = j
        else:
            result.append(lines[i])
            i += 1

    return "\n".join(result)


def convert_figure_placeholders(text: str) -> str:
    """Convert [FIGURE: description] placeholders to LaTeX figure environments."""
    def replace_figure(m):
        desc = m.group(1).strip()
        return (
            "\\begin{figure}[t]\n"
            "\\centering\n"
            "% \\includegraphics[width=\\linewidth]{figures/placeholder.pdf}\n"
            f"\\caption{{{desc}}}\n"
            "\\label{fig:placeholder}\n"
            "\\end{figure}"
        )

    return re.sub(r"\[FIGURE:\s*(.+?)\]", replace_figure, text)


def convert_math(text: str) -> str:
    """Ensure LaTeX math passes through correctly."""
    # Display math: $$...$$ -> \[...\]
    text = re.sub(r"\$\$(.+?)\$\$", r"\\[\1\\]", text, flags=re.DOTALL)
    return text


def convert_lists(text: str) -> str:
    """Convert Markdown bullet lists to LaTeX itemize."""
    lines = text.split("\n")
    result = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            if not in_list:
                result.append("\\begin{itemize}")
                in_list = True
            result.append(f"  \\item {stripped[2:]}")
        else:
            if in_list:
                result.append("\\end{itemize}")
                in_list = False
            result.append(line)

    if in_list:
        result.append("\\end{itemize}")

    return "\n".join(result)


def convert_code_blocks(text: str) -> str:
    """Remove or convert code blocks."""
    # Algorithm blocks stay as-is (they should be written in LaTeX Algorithm format)
    # Generic code blocks -> verbatim
    def replace_code(m):
        lang = m.group(1) or ""
        code = m.group(2)
        if lang.strip() in ("", "text", "plaintext"):
            return f"\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}"
        return f"\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}"

    return re.sub(r"```(\w*)\n(.*?)```", replace_code, text, flags=re.DOTALL)


def build_latex(title: str, body: str, venue: str, bib_path: str | None) -> str:
    """Assemble the full LaTeX document."""
    config = VENUE_CONFIGS[venue]
    is_ieee = venue.startswith("iccse")

    parts = [config["documentclass"], ""]
    parts.extend(config["packages"])
    parts.append("")
    parts.append(f"\\title{{{title or 'Untitled'}}}")
    parts.append("")

    if is_ieee:
        parts.append("% TODO: Fill in author names and affiliations")
        parts.append("\\author{")
        parts.append("  \\IEEEauthorblockN{First Author}")
        parts.append("  \\IEEEauthorblockA{Affiliation \\\\ Email}")
        parts.append("  \\and")
        parts.append("  \\IEEEauthorblockN{Second Author}")
        parts.append("  \\IEEEauthorblockA{Affiliation \\\\ Email}")
        parts.append("}")
    else:
        parts.append("% TODO: Add authors after acceptance (double-blind)")
        parts.append("\\author{Anonymous}")

    parts.append("")
    parts.append("\\begin{document}")
    parts.append("\\maketitle")
    parts.append("")

    # Extract abstract if present
    abstract_match = re.search(
        r"\\section\{Abstract\}\s*\n(.*?)(?=\\section\{)", body, re.DOTALL
    )
    if abstract_match:
        abstract_text = abstract_match.group(1).strip()
        parts.append("\\begin{abstract}")
        parts.append(abstract_text)
        parts.append("\\end{abstract}")
        parts.append("")
        body = body.replace(abstract_match.group(0), "")

    parts.append(body)
    parts.append("")

    if bib_path:
        bib_name = Path(bib_path).stem
        parts.append(f"\\bibliographystyle{{{config['bibstyle']}}}")
        parts.append(f"\\bibliography{{{bib_name}}}")
    parts.append("")
    parts.append("\\end{document}")

    return "\n".join(parts)


def convert(input_path: str, output_path: str, venue: str, bib_path: str | None) -> None:
    """Full conversion pipeline."""
    md_text = Path(input_path).read_text(encoding="utf-8")

    NATBIB_VENUES = {"neurips_2026", "icml_2026", "iclr_2026", "acl_2026"}

    text = convert_code_blocks(md_text)
    text = convert_citations(text, use_natbib=(venue in NATBIB_VENUES))
    title, text = convert_headings(text)
    text = convert_bold_italic(text)
    text = convert_tables(text)
    text = convert_figure_placeholders(text)
    text = convert_math(text)
    text = convert_lists(text)

    # Escape special LaTeX characters in regular text (not in commands)
    # Only escape % and & that aren't already escaped
    text = re.sub(r"(?<!\\)%", r"\\%", text)
    text = re.sub(r"(?<!\\)&(?!\\)", r"\\&", text)

    latex = build_latex(title, text, venue, bib_path)

    Path(output_path).write_text(latex, encoding="utf-8")
    print(f"Converted: {input_path} -> {output_path} (venue: {venue})")


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown paper to LaTeX")
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("output", help="Output LaTeX file")
    parser.add_argument(
        "--venue",
        default="neurips_2026",
        choices=list(VENUE_CONFIGS.keys()),
        help="Target conference template",
    )
    parser.add_argument("--bib", default=None, help="BibTeX file path")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    convert(args.input, args.output, args.venue, args.bib)


if __name__ == "__main__":
    main()
