def divide(a: float, b: float) -> float:
    """
    Simple example with a passing docstring test block.

    ```python test
    assert divide(6, 3) == 2
    ```
    """
    return a / b


class Greeter:
    """
    A class example whose method includes a docstring test block.
    """

    def greet(self, name: str) -> str:
        """
        Returns a greeting.

        ```python test
        g = Greeter()
        assert g.greet("World") == "Hello, World!"
        ```
        """
        return f"Hello, {name}!"
