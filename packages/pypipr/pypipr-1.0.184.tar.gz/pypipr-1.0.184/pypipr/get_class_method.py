def get_class_method(cls):
    """
    Mengembalikan berupa tuple yg berisi list dari method dalam class

    ```python
    class ExampleGetClassMethod:
        def a():
            return [x for x in range(10)]

        def b():
            return [x for x in range(10)]

        def c():
            return [x for x in range(10)]

        def d():
            return [x for x in range(10)]

    print(get_class_method(ExampleGetClassMethod))
    print(list(get_class_method(ExampleGetClassMethod)))
    ```
    """
    for x in dir(cls):
        a = getattr(cls, x)
        if not x.startswith("__") and callable(a):
            yield a
