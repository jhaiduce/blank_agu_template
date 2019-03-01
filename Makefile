PROJNAME=paper
SUBDIRS=
PDFFILES=$(PROJNAME).pdf $(PROJNAME)_si.pdf
PROD_TEX_FILES=$(PROJNAME).submit.tex $(PROJNAME)_si.submit.tex

# You want latexmk to *always* run, because make does not have all the info.
# Also, include non-file targets in .PHONY so they are run regardless of any
# file of the given name existing.
.PHONY: $(PROJNAME).pdf $(PDFFILES) all clean $(PROD_TEX_FILES)

# The first rule in a Makefile is the one executed by default ("make"). It
# should always be the "all" rule, so that "make" and "make all" are identical.
all: $(PDFFILES) $(PROJNAME)_diff.pdf $(PROD_TEX_FILES)

$(SUBDIRS):
	$(MAKE) -C $@

# MAIN LATEXMK RULE

# -pdf tells latexmk to generate PDF directly (instead of DVI).
# -pdflatex="" tells latexmk to call a specific backend with specific options.
# -use-make tells latexmk to call make for generating missing files.

# -interactive=nonstopmode keeps the pdflatex backend from stopping at a
# missing file reference and interactively asking you for an alternative.

$(PDFFILES): %.pdf: %.tex $(SUBDIRS)
	latexmk -pdf -pdflatex="pdflatex -interactive=nonstopmode" -use-make $<

$(PROJNAME)_diff.pdf: $(PROJNAME).tex
	./run-latexdiff.sh --main $(PROJNAME).tex -o $(PROJNAME)_diff.pdf HEAD

$(PROD_TEX_FILES): %.submit.tex: %.tex
	python AguTexPrep.py $<

clean:
	latexmk -C
