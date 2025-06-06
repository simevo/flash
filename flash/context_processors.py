from config import version


def add_variables_to_context(request):
    return {
        "version": version.__version__,
    }
