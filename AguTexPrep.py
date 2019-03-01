#!/usr/bin/env python
'''
This script alters an AGU manuscript LaTeX-source file to prepare for 
submission.  Specifically, it performs the following tasks, all required
by AGU journals during the submission process:

1) Turns off graphicx-commands in the preamble.
2) Disables the inclusion of graphics in figures.
3) Rename figures 'figNN.jpg', where NN is the figure number.
4) Replaces BibTeX commands with the full explicit bibliography.
5) Replaces any \input{filename} commands with the contents of filename.
6) Detects non-ascii characters, a common LaTeX formatting mistake.

The edited text file is saved as [filename].submit.tex
The resulting file can be built into a PDF using repeated calls to pdflatex
(or a similar executable) WITHOUT BibTeX steps, etc., making it appropriate
for submission to journals.

USAGE:
 AguTexPrep [options] [filename.tex]

OPTIONS:
 -h or -help:
     Print this help.
 -figs:
       The figures will be copied into a new directory called "ordered_figures".

 -showfigs:
       Graphics commands will not be commented out.
'''

import os
import re
from sys import argv
from shutil import copy
import datetime as dt

# Important variables:
iFig = 1
iSFig = 1
HideFigs = True
infile   = False
bibfile  = False
isDraft  = False
isLineno = False
DoRenameFigs=True

def find_graphics_file(nameFig):
    from glob import glob
    matches=glob(nameFig+'*')
    for match in matches:
        searchExtensions=['pdf','png','jpg','mps','jpeg','jbig2','jb2']
        extension=''
        for ext in searchExtensions:
            if match.lower().endswith(ext):
                extension=ext
                break
        if extension!='': break
    else:
        print 'WARNING: No file found to match pattern '+nameFig+'*'
    nameFig=match
    ext    = nameFig.split('.')[-1]

    return nameFig,ext

def process_tex_lines(TexFileName, out):
    '''
    For a LaTeX file named *TexFileName*, go through each line and make
    changes required by AGU submission standards.  Output will be placed into
    the file object (not file name!), *out*.

    If an input command is detected, this function is called recursively
    so that the separate file is absorbed by the top-level file.
    '''
    from string import ascii_uppercase as chars

    # Open file object.
    source = open(TexFileName, 'r')
    
    # Useful vars:
    InsideFigure = False
    global iFig, iSFig
    
    for iLine, line in enumerate(source):
        # Watch out for crazy readline chars.
        l = line.replace('\r\n', '\n')

        # Detect non-ascii characters:
        try:
            l.decode('ascii')
        except UnicodeDecodeError:
            print('WARNING: Non-ascii character in {}, line {}'.format(
                TexFileName, iLine+1))
            print('  >> '+l[:-1])
        
        # Comment out graphics lines:
        if 'graphicx' in l:
            out.write('%'*HideFigs+l)
        elif r'\setkeys{Gin}' in l:
            out.write('%'*HideFigs+l)

        # Replace bibliography:
        elif r'\bibliographystyle' in l:
            out.write('%'+l)

        elif r'\bibliography' in l and bibfile:
            for bibline in open(bibfile, 'r'): out.write(bibline)
            
        # Replace input commands with contents of input files:
        elif r'\input' in l:
            inputfile = re.search('\{(.+)\}', l).groups()[0]
            
            # LaTeX will automatically append a .tex extension if needed,
            # so we do the same
            if not os.path.isfile(inputfile) and \
               os.path.isfile(inputfile+'.tex'):
                inputfile=inputfile+'.tex'
                
            process_tex_lines(inputfile, out)
            out.write('\n')

        # Take note when we enter a figure block.
        elif r'\begin{figure}' in l:
            # If commented out, just dump to file and move on.
            if '%' in l[:l.find(r'\begin{figure}')]:
                out.write(l)
                continue

            # Otherwise, keep on moving on.
            fig_old_paths = []
            fig_new_paths = []
            fig_lines     = []; fig_lines.append(l)
            InsideFigure = True

        # When we leave a figure block, rename all figures.
        elif r'\end{figure}' in l:
            # If commented out, just dump to file and move on.
            if '%' in l[:l.find(r'\end{figure}')]:
                out.write(l)
                continue

            InsideFigure = False
            fig_lines.append(l)
            IsSubFigs = len(fig_old_paths)>1
        
            # Create new figure names.  Account for multiple graphics commands.
            # If requested via -figs flags, copy figures to ordered_figs folder.
            for iSub, nameFig in enumerate(fig_old_paths):
                nameFig,ext=find_graphics_file(nameFig)
                fignum = '{:02d}'.format(iFig) + chars[iSub]*IsSubFigs
                newFig = 'ordered_figures/fig{}.{}'.format(fignum,ext)
                fig_new_paths.append(newFig)
                if DoRenameFigs: copy(nameFig, newFig)
            iFig+=1

            # Write figure block to file with new figure names.
            i = 0
            for figline in fig_lines:
                if r'\includegraphics' in figline:
                    out.write('%'*HideFigs + figline.replace(fig_old_paths[i],
                                                             fig_new_paths[i]))
                    i += 1
                else:
                    out.write(figline)
                
            # Comment out include graphics, replace figure names:
        elif r'\includegraphics' in l:
            # If commented out, just dump to file and move on.
            if '%' in l[:l.find(r'\includegraphics')]:
                out.write(l)
                continue
            print l
            nameFig = re.search('{\"?(.+(\.\w+)?)\"?}', l).groups()[0]
            if InsideFigure:
                fig_old_paths.append(nameFig)
                fig_lines.append(l)#'%'+l.replace(nameFig, newFig))
            else:
                print('LINE: ', l)
                print('Found graphics outside of Figure block')
                fignum = 'S{:02d}'.format(iSFig)
                figFile,ext=find_graphics_file(nameFig)
                newFig = 'ordered_figures/fig{}.{}'.format(fignum,ext)

                if DoRenameFigs:
                    copy(figFile, newFig)
                    out.write('%'+l.replace(nameFig,newFig))
                else:
                    out.write(l)
                iSFig+=1

        # Buffer lines when inside a figure block:
        elif InsideFigure:
            fig_lines.append(l)
        
        # No change (write line!):
        else:
            out.write(l)

    # Close input file and return.
    source.close()
    return True

# Start by handling arguments.
for option in argv[1:]:
    # Handle options:
    if option == '-h' or option == '-help':
        print __doc__
        exit()
    elif option == '-figs':
        DoRenameFigs=True
    elif option == '-showfigs':
        HideFigs=False
    else:
        infile = option

if not infile:
    raise(ValueError('No input file given.'))
if not os.path.isfile(infile):
    raise(ValueError('Input file does not exist.'))
if '.tex' not in infile:
    raise(ValueError('Input file is not a LaTeX source file.'))

bibfile=infile[:-3]+'bbl'
if not os.path.isfile(bibfile):
    print('WARNING: I cannot find {}.  Did you compile the document?'.format(bibfile))

if DoRenameFigs and not os.path.isdir('ordered_figures'):
    os.mkdir('ordered_figures')
    
# Open output file.
out = open(infile[:-3]+'submit.tex'.format(
        dt.datetime.now()), 'w')

# Parse and alter LaTeX file:
process_tex_lines(infile, out)

# Close output file.
out.close()
