// Division On Mac M2 with ARM ISA

.data

_a:
    .byte 0x7f

_b:
    .byte 0x02

_length:
    .byte 0x08




.text
    .global _main
    .p2align 2

    _main:
        stp x29, x30, [sp, #-16]!
        mov x29, sp
        sub sp, sp, #16

    // load a to x0 reg
    adrp x1, _a@PAGE
    add x1, x1, _a@PAGEOFF
    ldrb w0, [x1]

    // load b to x3 reg
    adrp x2, _b@PAGE
    add x2, x2, _b@PAGEOFF
    ldrb w3, [x2]

    // judge if b is 0

    cbz x3, L_div_zero

    // div calculate
    mov x4, #7
    lsl x5, x3, x4
    mov x6, #0

    L_bit_loop:
        cmp x0, x5
        b.lo L_next_bit

        sub x0,x0,x5

        mov x7, #1
        lsl x7, x7, x4
        orr x6,x6, x7

    L_next_bit:
        lsr x5, x5, #1
        subs x4, x4, #1
        b.ge L_bit_loop




L_div_done:
        str x6, [sp]
        str x0, [sp, #8]

        adrp x0, L_format@PAGE
        add x0, x0, L_format@PAGEOFF
        bl _printf

        add sp, sp, #16
        ldp x29, x30, [sp], #16
        mov w0, #0
        ret

L_div_zero:
        adrp x0, L_zero_msg@PAGE
        add x0, x0, L_zero_msg@PAGEOFF
        bl _puts

        add sp, sp, #16
        ldp x29, x30, [sp], #16
        mov w0, #1
        ret

.section __TEXT,__cstring,cstring_literals
L_format:
    .asciz "quotient = %lu, remainder = %lu\n"

L_zero_msg:
    .asciz "err: divisor is zero"
