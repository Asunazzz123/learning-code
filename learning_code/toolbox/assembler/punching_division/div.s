.section __TEXT,__const
_input_length:
    .byte 64                      // 输入的总位数：1..64
_punch_length:
    .byte 8                       // 每组位数，整除总位数

.dss

_mod8_00:
    .byte 0

_mod8_01:
    .byte 0

.data
    .p2align 3
    .global _num1
_num1:
    .quad 0xad4a                  // 10101101 01001010 = 173*2^8 + 74
    .global _num2
_num2:
    .quad 0

.text
    .p2align 2
    .global _main
    .global _div
_main:
_div:
    stp x29, x30, [sp, #-16]!
    mov x29, sp

    // 先检查两个数，避免只输出一半后才发现第二个输入非法。
    adrp x1, _input_length@PAGE
    add x1, x1, _input_length@PAGEOFF
    ldrb w8, [x1]
    cbz x8, L_invalid
    cmp x8, #64
    b.hi L_invalid

    adrp x1, _punch_length@PAGE
    add x1, x1, _punch_length@PAGEOFF
    ldrb w9, [x1]
    cbz x9, L_invalid
    cmp x9, x8
    b.hi L_invalid
    udiv x10, x8, x9
    msub x11, x10, x9, x8         // input_length % punch_length
    cbnz x11, L_invalid

    adrp x1, _num1@PAGE
    add x1, x1, _num1@PAGEOFF
    ldr x0, [x1]                  // 读取完整 64 位，而不是 ldrb
    adrp x2, _num2@PAGE
    add x2, x2, _num2@PAGEOFF
    ldr x3, [x2]
    cmp x8, #64
    b.eq L_valid                  // 64 位时不能右移 64：寄存器移位会取模
    lsr x10, x0, x8
    lsr x11, x3, x8
    orr x10, x10, x11
    cbnz x10, L_invalid           // 总位数之外不能有非零位

L_valid:
    adrp x1, L_num1_name@PAGE
    add x1, x1, L_num1_name@PAGEOFF
    bl L_expand

    adrp x1, _num2@PAGE
    add x1, x1, _num2@PAGEOFF
    ldr x0, [x1]
    adrp x1, L_num2_name@PAGE
    add x1, x1, L_num2_name@PAGEOFF
    bl L_expand
    mov w0, #0
    b L_return

L_invalid:
    adrp x0, L_error@PAGE
    add x0, x0, L_error@PAGEOFF
    bl _puts
    mov w0, #1
L_return:
    ldp x29, x30, [sp], #16
    ret

// X0 = 无符号整数，X1 = 名称。由最高组到最低组输出，保留前导零组。
L_expand:
    stp x29, x30, [sp, #-64]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    stp x23, x24, [sp, #48]
    sub sp, sp, #16               // macOS printf 的可变参数放在栈上
    mov x19, x0
    adrp x2, _input_length@PAGE
    add x2, x2, _input_length@PAGEOFF
    ldrb w20, [x2]
    adrp x2, _punch_length@PAGE
    add x2, x2, _punch_length@PAGEOFF
    ldrb w21, [x2]
    sub x20, x20, x21             // 首组的右移位数 / 2 的指数
    mov x22, #-1
    mov x23, #64
    sub x23, x23, x21
    lsr x22, x22, x23             // 掩码：(1 << k) - 1，也支持 k=64

    str x1, [sp]
    adrp x0, L_heading@PAGE
    add x0, x0, L_heading@PAGEOFF
    bl _printf
L_group:
    lsr x23, x19, x20
    and x23, x23, x22             // ai = (N >> (k*i)) & mask
    stp x23, x20, [sp]
    adrp x0, L_term@PAGE
    add x0, x0, L_term@PAGEOFF
    bl _printf
    cbz x20, L_expand_done
    adrp x0, L_plus@PAGE
    add x0, x0, L_plus@PAGEOFF
    bl _printf
    sub x20, x20, x21
    b L_group
L_expand_done:
    adrp x0, L_newline@PAGE
    add x0, x0, L_newline@PAGEOFF
    bl _printf
    add sp, sp, #16
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #64
    ret

.section __TEXT,__cstring,cstring_literals
L_num1_name: .asciz "num1"
L_num2_name: .asciz "num2"
L_heading: .asciz "%s = "
L_term: .asciz "%llu*2^%llu"
L_plus: .asciz " + "
L_newline: .asciz "\n"
L_error: .asciz "Error: require 1 <= group bits <= input bits <= 64, input bits divisible by group bits, and numbers fitting input bits."

