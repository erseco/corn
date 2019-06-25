from types import ModuleType
from kombu.utils.imports import symbol_by_name
from contextlib import contextmanager
import os
import sys
import importlib
from vine.five import values


class NotAPackage(Exception):
    """Raised when importing a package, but it's not a package."""


@contextmanager
def cwd_in_path():
    """Context adding the current working directory to sys.path."""
    cwd = os.getcwd()
    if cwd in sys.path:
        yield
    else:
        sys.path.insert(0, cwd)
        try:
            yield cwd
        finally:
            try:
                sys.path.remove(cwd)
            except ValueError:  # pragma: no cover
                pass


def find_module(module, path=None, imp=None):
    """Version of :func:`imp.find_module` supporting dots."""
    if imp is None:
        imp = importlib.import_module
    with cwd_in_path():
        try:
            return imp(module)
        except ImportError:
            # Raise a more specific error if the problem is that one of the
            # dot-separated segments of the module name is not a package.
            if '.' in module:
                parts = module.split('.')
                for i, part in enumerate(parts[:-1]):
                    package = '.'.join(parts[:i + 1])
                    try:
                        mpart = imp(package)
                    except ImportError:
                        # Break out and re-raise the original ImportError
                        # instead.
                        break
                    try:
                        mpart.__path__
                    except AttributeError:
                        raise NotAPackage(package)
            raise


def import_from_cwd(module, imp=None, package=None):
    """Import module, temporarily including modules in the current directory.

    Modules located in the current directory has
    precedence over modules located in `sys.path`.
    """
    if imp is None:
        imp = importlib.import_module
    with cwd_in_path():
        return imp(module, package=package)


def find_app(app, symbol_by_name=symbol_by_name, imp=import_from_cwd):
    """Find app by name."""
    from ..base import Corn

    try:
        sym = symbol_by_name(app, imp=imp)
    except AttributeError:
        # last part was not an attribute, but a module
        sym = imp(app)
    if isinstance(sym, ModuleType) and ':' not in app:
        try:
            found = sym.app
            if isinstance(found, ModuleType):
                raise AttributeError()
        except AttributeError:
            try:
                found = sym.corn
                if isinstance(found, ModuleType):
                    raise AttributeError()
            except AttributeError:
                if getattr(sym, '__path__', None):
                    try:
                        return find_app(
                            '{0}.corn'.format(app),
                            symbol_by_name=symbol_by_name, imp=imp,
                        )
                    except ImportError:
                        pass
                for suspect in values(vars(sym)):
                    if isinstance(suspect, Corn):
                        return suspect
                raise
            else:
                return found
        else:
            return found
    return sym
