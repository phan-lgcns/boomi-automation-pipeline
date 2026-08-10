def solution(expressions):
    answer = []

    def to_base(n, base):
        if n == 0:
            return "0"

        digits = []
        while n:
            digits.append(str(n % base))
            n //= base

        return ''.join(reversed(digits))

    expression_array = []
    for exp in expressions:
        arr = exp.split(" ")
        num1, sign, num2, equal, num3 = arr
        if num3 != "X":
            expression_array.append([int(num1), sign, int(num2), int(num3)])
        else:
            expression_array.append([int(num1), sign, int(num2), num3])

    s = "".join(expressions)
    min_base = 1
    for c in s:
        if c.isdigit():
            min_base = max(min_base, int(c) + 1)
    
    def is_correct(num1, sign, num2, num3, base):
        num1 = int(str(num1), base = base)
        num2 = int(str(num2), base = base)
        num3 = int(str(num3), base = base)
        if sign == "+":
            return num1 + num2 == num3
        else:
            return num1 - num2 == num3
        return True
    
    real_base = []
    for base in range(9, min_base - 1, -1):
        correct = True
        for num1, sign, num2, num3 in expression_array:
            if num3 != "X" and not is_correct(num1, sign, num2, num3, base):
                correct = False
        if correct:
            real_base.append(base)
    
    for exp in expression_array:
        if exp[3] == "X":
            if len(real_base) > 1:
                exp[3] = "?"
            elif sign == "+":
                exp[3] = to_base(int(str(exp[0]), base = real_base[0]) + int(str(exp[2]), base = real_base[0]), real_base[0])
            else:
                exp[3] = to_base(int(str(exp[0]), base = real_base[0]) - int(str(exp[2]), base = real_base[0]), real_base[0])
    return expression_array, real_base


print(solution(["10 - 2 = X", "30 + 31 = 101", "3 + 3 = X", "33 + 33 = X"]))