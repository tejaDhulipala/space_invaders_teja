b = 0


def a():
    nonlocal b
    b += 1


a()
print(b)
