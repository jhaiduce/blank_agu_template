cmake_minimum_required(VERSION 3.17.1)

project(AGU_template LANGUAGES)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/UseLatexMk")

include(UseLatexMk)

string(TIMESTAMP TODAY "%Y%m%d")

add_latex_document(SOURCE paper.tex TARGET paper)

add_custom_command(TARGET paper
  COMMAND ${CMAKE_COMMAND} -E copy paper.pdf paper_${TODAY}.pdf)
