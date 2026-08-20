.text
.globl _main
.p2align 2

_main:

    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16 // 申请16字节空间

    mov w8, #10 //  立即数10写入w8
    mov w9, #20 //  立即数20写入w9
    add w8, w8, w9 // 加法

    str w8, [sp]
    adrp x0, format@PAGE
    add x0, x0, format@PAGEOFF
    bl _printf



    add sp, sp, #16 // 释放16字节空间
    mov w0, #0
    ldp x29, x30, [sp], #16
    ret

    loop_forever:
        b loop_forever

.section __TEXT,__cstring,cstring_literals
format:
    .asciz "%d\n"