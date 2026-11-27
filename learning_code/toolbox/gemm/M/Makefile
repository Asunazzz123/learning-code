METAL := xcrun --sdk macosx metal

.PHONY: all run clean

all: build/gemm.metallib

run: build/gemm build/gemm.metallib
	./build/gemm

build/gemm: main.mm | build
	xcrun --sdk macosx clang++ -std=c++17 -fobjc-arc $< -framework Foundation -framework Metal -o $@

build/gemm.metallib: build/gemm.ir
	$(METAL) $< -o $@

build/gemm.ir: gemm.metal | build
	$(METAL) -c $< -o $@

build:
	mkdir -p $@

clean:
	rm -f build/gemm build/gemm.ir build/gemm.metallib
