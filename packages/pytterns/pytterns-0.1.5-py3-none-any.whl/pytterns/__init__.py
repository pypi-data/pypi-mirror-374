from pytterns.core.decorators import strategy, chain, observer, factory, command
from pytterns.patterns import load

"""
Provide a runtime __version__ without hard-coding a release version.

We prefer a generated `_version.py` written by setuptools_scm. If that's
not present, try to read the installed package version via importlib.metadata.
As a final fallback (e.g., during local development with no tags) use a
neutral placeholder so setuptools_scm can still control released versions.
"""

__version__ = None

try:
	# Prefer generated version file from setuptools_scm if present
	from ._version import __version__ as _scm_version
	__version__ = _scm_version
except Exception:
	try:
		from importlib.metadata import version, PackageNotFoundError
		try:
			__version__ = version('pytterns')
		except PackageNotFoundError:
			# No installed distribution available; leave neutral fallback
			__version__ = '0+unknown'
	except Exception:
		# importlib.metadata not available (very old Python); use neutral fallback
		__version__ = '0+unknown'
