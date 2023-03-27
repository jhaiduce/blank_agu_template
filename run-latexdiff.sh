git latexdiff --no-cleanup --prepare 'echo Copying from '"$PWD"' to $PWD; rsync -avL --exclude=.git --exclude=build --include=\*/ --include=\*.pdf --include=tables/\*.tex --include=\*.ini --exclude=\* '"$PWD"'/ .' --ignore-makefile --latexmk $@
