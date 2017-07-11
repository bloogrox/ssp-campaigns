import os


if os.environ.get("ENV_TYPE") == "ci":
    from .ci import *  # NOQA
    print("Using CI settings")
else:
    try:
        from .local import *  # NOQA
        print("Using LOCAL settings")
    except ImportError:
        from .prod import *  # NOQA
        print("Using PROD settings")
