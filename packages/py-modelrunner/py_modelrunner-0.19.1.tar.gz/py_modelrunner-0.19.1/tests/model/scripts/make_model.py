import modelrunner


def do_not_calculate(a=1, b=2):
    """This function should not be run."""
    raise RuntimeError("This must not run")


@modelrunner.make_model
def calculate(a=1, b=2):
    """This function has been marked as a model."""
    return a * b
