import contextlib

with contextlib.suppress(ImportError):
    from . import db
