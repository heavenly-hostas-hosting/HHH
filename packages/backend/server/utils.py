import os


def assure_get_env(var: str) -> str:
    """Get an environment variable or raise an error if it is not set."""
    value = os.getenv(var)
    if value is None:
        msg = f"Environment variable '{var}' is not set."
        raise OSError(msg)
    return value
