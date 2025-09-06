# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
import warnings

def warn_user(message: str):
    warnings.formatwarning = lambda msg, cat, fname, lno, line=None: f"{cat.__name__}: {msg}\n"
    warnings.warn(message, UserWarning, stacklevel=2)

# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
