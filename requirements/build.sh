#!/bin/bash
#
# Build a latex file and render to pdf.
#

# Specify name of the latex file to build.
MAIN_FILE="specification"

# Specify the name of the output pdf.
OUT_FILE="specification"

# Clean up the build environment.
function cleanup {
   rm -f *.aux *.bbl *.blg *.dvi *.log *.out *.toc
}

# Essential for a reliable rebuild.
cleanup

# Proceed to build the output file.
pdflatex -interaction=nonstopmode $MAIN_FILE

# Only proceed with remaining build stages if the above build was successful.
if [ $? -eq 0 ]; then
	# Generate bbl from aux.
	bibtex $MAIN_FILE
	# Final builds to generate TOC, references etc.
	pdflatex -interaction=nonstopmode $MAIN_FILE
	pdflatex -interaction=nonstopmode $MAIN_FILE
	# Not required, but keeps the directory free of messy files.
	cleanup
	# Rename output file.
	mv $MAIN_FILE.pdf $OUT_FILE.pdf
	evince $OUT_FILE.pdf
fi
