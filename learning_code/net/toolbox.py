def _as_binary_digits(value, name):
    digits = str(value)
    if not digits or any(digit not in "01" for digit in digits):
        raise ValueError(f"{name} must contain only binary digits 0 and 1")
    return digits


def division(a, b):
    dividend = _as_binary_digits(a, "dividend")
    divisor = _as_binary_digits(b, "divisor")
    if set(divisor) == {"0"}:
        raise ZeroDivisionError("divisor cannot be zero")

    work = [int(bit) for bit in dividend]
    divisor_bits = [int(bit) for bit in divisor]
    divisor_len = len(divisor_bits)

    for i in range(len(work) - divisor_len + 1):
        if work[i] == 0:
            continue
        for j, bit in enumerate(divisor_bits):
            work[i + j] ^= bit

    remainder_len = divisor_len - 1
    if remainder_len == 0:
        return ""
    remainder = "".join(str(bit) for bit in work[-remainder_len:])
    return remainder.zfill(remainder_len)

if __name__ == "__main__":
    print(division(11010110110000, 10011))
