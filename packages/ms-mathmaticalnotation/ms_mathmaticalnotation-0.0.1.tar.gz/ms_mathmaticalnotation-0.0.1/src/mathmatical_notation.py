class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

def evalPrefix(tokens):
    stack = Stack()
    for token in reversed(tokens):
        if token in "+-*/":
            a = stack.pop()
            b = stack.pop()
            if token == "+":
                stack.push(a + b)
            elif token == "-":
                stack.push(a - b)
            elif token == "*":
                stack.push(a * b)
            elif token == "/":
                stack.push(int(a / b))
        else:
            stack.push(int(token))
    return stack.pop()

def evalRPN(tokens):
    stack = Stack()
    for token in tokens:
        if token in "+-*/":
            a = stack.pop()
            b = stack.pop()
            if token == "+":
                stack.push(b + a)
            elif token == "-":
                stack.push(b - a)
            elif token == "*":
                stack.push(b * a)
            elif token == "/":
                stack.push(int(b / a))
        else:
            stack.push(int(token))
    return stack.pop()

def smartEval(tokens):
    if tokens[0] in "+-*/":
        print("🔍 تشخیص داده شد: پریفیکس")
        return evalPrefix(tokens)
    elif tokens[-1] in "+-*/":
        print("🔍 تشخیص داده شد: پسوندی (RPN)")
        return evalRPN(tokens)
    else:
        raise ValueError("نوع عبارت قابل تشخیص نیست!")
