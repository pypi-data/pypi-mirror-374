"""Main module for my-sample-pkg."""

import sys


def hello():
    """Print a greeting message to PyPI."""
    print("Hello, PyPI!")


def greet():
    """Greet with name from command line arguments."""
    if len(sys.argv) > 1:
        name = " ".join(sys.argv[1:])
        print(f"Hello, {name}!")
    else:
        print("Hello, World!")


def count():
    """Count from 1 to N where N is from command line arguments."""
    try:
        if len(sys.argv) > 1:
            n = int(sys.argv[1])
            for i in range(1, n + 1):
                print(f"Count: {i}")
        else:
            print("Usage: count <number>")
    except ValueError:
        print("Error: Please provide a valid number")


def echo():
    """Echo all command line arguments."""
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        print(f"Echo: {message}")
    else:
        print("Usage: echo <message>")


if __name__ == "__main__":
    hello()