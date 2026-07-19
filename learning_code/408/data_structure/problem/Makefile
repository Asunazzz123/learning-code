#Makefile

CXX ?= g++
Mode ?= Debug
File ?=


build:
	$(CXX) $(File).cpp -o $(File).o -D$(Mode)
	./$(File).o
	rm $(File).o
