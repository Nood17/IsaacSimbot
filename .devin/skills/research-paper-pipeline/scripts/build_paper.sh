#!/bin/bash
# Build LaTeX paper to PDF.
# Handles multiple compilation passes for cross-references and bibliography.
#
# Usage:
#   bash build_paper.sh output/paper.tex
#   bash build_paper.sh output/paper.tex --clean

set -e

if [ -z "$1" ]; then
    echo "Usage: bash build_paper.sh <tex_file> [--clean]"
    exit 1
fi

TEX_FILE="$1"
TEX_DIR=$(dirname "$TEX_FILE")
TEX_NAME=$(basename "$TEX_FILE" .tex)

cd "$TEX_DIR"

if [ "$2" = "--clean" ]; then
    echo "Cleaning auxiliary files..."
    rm -f "${TEX_NAME}".{aux,bbl,blg,log,out,toc,lof,lot,fls,fdb_latexmk,synctex.gz}
    echo "Done."
    exit 0
fi

if ! command -v pdflatex &> /dev/null; then
    echo "Error: pdflatex not found. Install a TeX distribution (e.g., MacTeX, TeX Live)."
    exit 1
fi

echo "=== Pass 1: pdflatex ==="
pdflatex -interaction=nonstopmode "${TEX_NAME}.tex" || true

if [ -f "${TEX_NAME}.aux" ] && command -v bibtex &> /dev/null; then
    echo "=== Pass 2: bibtex ==="
    bibtex "${TEX_NAME}" || true
fi

echo "=== Pass 3: pdflatex ==="
pdflatex -interaction=nonstopmode "${TEX_NAME}.tex" || true

echo "=== Pass 4: pdflatex (final) ==="
pdflatex -interaction=nonstopmode "${TEX_NAME}.tex" || true

if [ -f "${TEX_NAME}.pdf" ]; then
    echo ""
    echo "Success: ${TEX_DIR}/${TEX_NAME}.pdf"
else
    echo ""
    echo "Error: PDF not generated. Check ${TEX_NAME}.log for details."
    exit 1
fi
