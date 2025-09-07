#!/usr/bin/env python3
"""This example shows how a collection of results can be read.

.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de>
"""

from pathlib import Path

from modelrunner import ResultCollection, make_model_class


def multiply(a: float = 1, b: float = 2):
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    # create model class
    model = make_model_class(multiply)

    # write data
    Path("data").mkdir(parents=True)
    for n, a in enumerate(range(5, 10)):
        result = model({"a": a}).get_result()
        result.to_file(f"data/test_{n}.json")

    # read data
    rc = ResultCollection.from_folder("data")
    print(rc.as_dataframe())
