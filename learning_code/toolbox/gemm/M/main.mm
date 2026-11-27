#import <Foundation/Foundation.h>
#import <Metal/Metal.h>

#include <cstdio>

int main() {
    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            std::fprintf(stderr, "No Metal device available\n");
            return 1;
        }

        NSError* error = nil;
        NSURL* libraryURL = [NSURL fileURLWithPath:@"build/gemm.metallib"];
        id<MTLLibrary> library = [device newLibraryWithURL:libraryURL error:&error];
        if (!library) {
            std::fprintf(stderr, "Could not load gemm.metallib: %s\n",
                         error.localizedDescription.UTF8String);
            return 1;
        }

        id<MTLFunction> function = [library newFunctionWithName:@"dot2"];
        if (!function) {
            std::fprintf(stderr, "Could not find the dot2 kernel\n");
            return 1;
        }

        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:function
                                                                                   error:&error];
        if (!pipeline) {
            std::fprintf(stderr, "Could not create the compute pipeline: %s\n",
                         error.localizedDescription.UTF8String);
            return 1;
        }

        id<MTLBuffer> output = [device newBufferWithLength:sizeof(int)
                                                 options:MTLResourceStorageModeShared];
        id<MTLCommandQueue> queue = [device newCommandQueue];
        id<MTLCommandBuffer> command = [queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [command computeCommandEncoder];
        if (!output || !encoder) {
            std::fprintf(stderr, "Could not prepare the Metal dispatch\n");
            return 1;
        }

        const MTLSize oneThread = MTLSizeMake(1, 1, 1);
        [encoder setComputePipelineState:pipeline];
        [encoder setBuffer:output offset:0 atIndex:0];
        [encoder dispatchThreads:oneThread threadsPerThreadgroup:oneThread];
        [encoder endEncoding];
        [command commit];
        [command waitUntilCompleted];
        if (command.status != MTLCommandBufferStatusCompleted) {
            std::fprintf(stderr, "dot2 failed: %s\n",
                         command.error.localizedDescription.UTF8String);
            return 1;
        }

        std::printf("%d\n", *static_cast<const int*>(output.contents));
        return 0;
    }
}
