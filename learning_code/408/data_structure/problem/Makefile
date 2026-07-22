#Makefile

CXX ?= g++
Mode ?= Debug
File ?=
std ?=c++17

fpath := $(shell find . -type f \
	\( -name "$(File).cpp" -o -name "$(File).c" \) \
	-print -quit)

build:
	$(CXX) -std=$(std) $(fpath) -o $(File).o -D$(Mode)
	./$(File).o
	rm $(File).o
