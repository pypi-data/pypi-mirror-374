
__all__ = ["hello", "__version__"]
__version__ = "0.1.0"

def hello(name: str = "world") -> str:
    return f"Hello, {name}!"
