cmake_minimum_required(VERSION 3.17.1)

project(AGU_template LANGUAGES)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/UseLatexMk")

set(TEXFILE paper.tex)

get_filename_component(TEXFILE_BASENAME ${TEXFILE} NAME_WE)

include(UseLatexMk)

string(TIMESTAMP TODAY "%Y%m%d")

add_latex_document(SOURCE ${TEXFILE} TARGET ${TEXFILE_BASENAME})

add_custom_command(OUTPUT ${TEXFILE_BASENAME}_${TODAY}.pdf
  COMMAND ${CMAKE_COMMAND} -E copy ${TEXFILE_BASENAME}.pdf ${TEXFILE_BASENAME}_${TODAY}.pdf)

add_custom_target(timestamped_pdf DEPENDS ${TEXFILE_BASENAME}_${TODAY}.pdf)

add_custom_command(OUTPUT ${TEXFILE_BASENAME}_diff.pdf
  COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/run-latexdiff.sh --main ${TEXFILE} -o ${CMAKE_CURRENT_BINARY_DIR}/${TEXFILE_BASENAME}_diff.pdf HEAD
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

add_custom_target(diffed_paper DEPENDS ${TEXFILE_BASENAME}_diff.pdf)
