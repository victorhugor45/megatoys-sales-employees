def foobar(n, texto):
    for i in range(1, n+1):
        if i % 3 == 0:
            print("Foo")
        if i % 5 == 0:
            print("Bar")
            print(texto)
        if i % 3 == 0 and i % 5 == 0:
            print("FooBar")

foobar(100, "¡Monda!")

