import importlib.util
import sys as _sys
import sys
import types
from datetime import datetime, timedelta

from pathlib import Path

# Ensure package imports resolve to the source tree (determine path dynamically)
_here = Path(__file__).resolve()
# backend/tests/boilerplates -> go up two levels to backend, then into src
src_dir = _here.parents[2] / 'src'
repo_root = _here.parents[3]
tests_dir = _here.parents[1]
# Add repository root and test directories to sys.path so imports resolve
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(tests_dir))
# Also add the backend directory (parent of src) so `import src...` works
backend_dir = src_dir.parent
sys.path.insert(0, str(backend_dir))
# And keep src_dir on the path so `import libs...` works too
sys.path.insert(0, str(src_dir))


# Minimal display_tty mock
display_tty = types.ModuleType('display_tty')


class DummyDisp:
    def __init__(self, *a, **k):
        pass

    def update_disp_debug(self, *a, **k):
        pass

    def log_debug(self, *a, **k):
        pass

    def log_info(self, *a, **k):
        pass

    def log_warning(self, *a, **k):
        pass

    def log_error(self, *a, **k):
        pass

    def disp_print_debug(self, *a, **k):
        pass


def initialise_logger(name, flag=False):
    return DummyDisp()


display_tty.Disp = DummyDisp
display_tty.initialise_logger = initialise_logger
_sys.modules['display_tty'] = display_tty


# Minimal constants used by the boilerplates
const_mod = types.ModuleType('libs.utils.constants')
const_mod.TAB_CONNECTIONS = 'Connections'
const_mod.TAB_ACCOUNTS = 'Accounts'
const_mod.REQUEST_TOKEN_KEY = 'X-Token'
const_mod.REQUEST_BEARER_KEY = 'Authorization'
const_mod.JSON_TITLE = 'title'
const_mod.JSON_MESSAGE = 'message'
const_mod.JSON_RESP = 'resp'
const_mod.JSON_ERROR = 'error'
const_mod.JSON_LOGGED_IN = 'logged_in'
const_mod.UA_TOKEN_LIFESPAN = 3600
const_mod.RANDOM_MIN = 1
const_mod.RANDOM_MAX = 9
const_mod.ASSETS_DIRECTORY = Path(repo_root) / 'backend' / 'assets'
_sys.modules['libs.utils.constants'] = const_mod
_sys.modules['src.libs.utils.constants'] = const_mod


# Minimal HTTP codes helper (HCI) and default content type
http_mod = types.ModuleType('libs.http_codes')
HTTP_DEFAULT_TYPE = 'application/json'


class HCI:
    @staticmethod
    def invalid_token(content=None, content_type=None, headers=None):
        return ('invalid_token', content, headers, content_type)

    @staticmethod
    def bad_request(content=None, content_type=None, headers=None):
        return ('bad_request', content, headers, content_type)

    @staticmethod
    def not_found(content=None, content_type=None, headers=None):
        return ('not_found', content, headers, content_type)

    @staticmethod
    def unauthorized(content=None, content_type=None, headers=None):
        return ('unauthorized', content, headers, content_type)

    @staticmethod
    def internal_server_error(content=None, content_type=None, headers=None):
        return ('internal_server_error', content, headers, content_type)

    @staticmethod
    def forbidden(content=None, content_type=None, headers=None):
        return ('forbidden', content, headers, content_type)


_sys.modules['libs.http_codes'] = http_mod
_sys.modules['src.libs.http_codes'] = http_mod
http_mod.HCI = HCI
http_mod.HTTP_DEFAULT_TYPE = HTTP_DEFAULT_TYPE


class HttpDataTypes:
    JSON = HTTP_DEFAULT_TYPE


http_mod.HttpDataTypes = HttpDataTypes


# Minimal ServerHeaders
server_header_mod = types.ModuleType('libs.server_header')


class ServerHeaders:
    def for_json(self):
        return {'content-type': HTTP_DEFAULT_TYPE}


server_header_mod.ServerHeaders = ServerHeaders
_sys.modules['libs.server_header'] = server_header_mod
_sys.modules['src.libs.server_header'] = server_header_mod


# Minimal FinalSingleton base class
core_mod = types.ModuleType('libs.core')


class FinalSingleton:
    def __init__(self):
        pass


core_mod.FinalSingleton = FinalSingleton


class FinalClass(type):
    pass


core_mod.FinalClass = FinalClass


class RuntimeControl:
    pass


core_mod.RuntimeControl = RuntimeControl
_sys.modules['libs.core'] = core_mod
_sys.modules['src.libs.core'] = core_mod


# Minimal runtime manager and RI singleton
runtime_mod = types.ModuleType('libs.core.runtime_manager')


class RuntimeManager:
    def __init__(self):
        self._registry = {}
        self._name_map = {}
        self._name_map_module = {}

    def register(self, cls, instance):
        self._registry[cls] = instance
        # also register by class name to aid lookups for aliased imports
        try:
            self._name_map[getattr(cls, '__name__', str(cls))] = instance
            self._name_map_module[(getattr(cls, '__module__', None), getattr(
                cls, '__name__', None))] = instance
        except Exception:
            pass

    def get(self, cls):
        # debug trace for registry lookups
        # print requested cls and registry keys to diagnose aliasing issues
        try:
            print(
                f"RuntimeManager.get: requested={getattr(cls, '__module__', None)}.{getattr(cls, '__name__', cls)}")
            print('RuntimeManager registry keys:', [
                  f"{getattr(k, '__module__', None)}.{getattr(k, '__name__', k)}" for k in self._registry.keys()])
        except Exception:
            pass
        if cls in self._registry:
            return self._registry.get(cls)
        # fallback: match by class name for cases where tests load the same
        # class object under a different module identity (aliases)
        cls_name = getattr(cls, '__name__', None)
        for k, v in self._registry.items():
            if getattr(k, '__name__', None) == cls_name:
                return v
        # last attempt: try module+name then fallback to name-only
        key = (getattr(cls, '__module__', None), cls_name)
        if key in self._name_map_module:
            return self._name_map_module.get(key)
        return self._name_map.get(cls_name)

    def get_if_exists(self, cls, default=None):
        try:
            print(
                f"RuntimeManager.get_if_exists: requested={getattr(cls, '__module__', None)}.{getattr(cls, '__name__', cls)}")
            print('RuntimeManager registry keys:', [
                  f"{getattr(k, '__module__', None)}.{getattr(k, '__name__', k)}" for k in self._registry.keys()])
        except Exception:
            pass
        if cls in self._registry:
            v = self._registry.get(cls)
            try:
                print(
                    f"RuntimeManager.get_if_exists: found exact instance={getattr(v, '__module__', None)}.{getattr(v, '__class__', v)}")
            except Exception:
                pass
            return v
        # fallback by name to handle aliased/duplicate class objects
        cls_name = getattr(cls, '__name__', None)
        for k, v in self._registry.items():
            # require both name and module to match to avoid cross-test collisions
            if getattr(k, '__name__', None) == cls_name and getattr(k, '__module__', None) == getattr(cls, '__module__', None):
                try:
                    print(
                        f"RuntimeManager.get_if_exists: matched by key name+module -> returning {getattr(v, '__module__', None)}.{getattr(v, '__class__', v)}")
                except Exception:
                    pass
                return v
        # first try module+name exact match
        key = (getattr(cls, '__module__', None), cls_name)
        if key in self._name_map_module:
            res = self._name_map_module.get(key)
        else:
            res = self._name_map.get(cls_name, default)
        try:
            print(
                f"RuntimeManager.get_if_exists: name_map lookup -> returning {getattr(res, '__module__', None)}.{getattr(res, '__class__', res)}")
        except Exception:
            pass
        return res


RI = RuntimeManager()
runtime_mod.RuntimeManager = RuntimeManager
runtime_mod.RI = RI
_sys.modules['libs.core.runtime_manager'] = runtime_mod
# also register under src namespace
_sys.modules['src.libs.core.runtime_manager'] = runtime_mod

# Expose RuntimeManager and RI on libs.core as some modules import them from there
core_mod.RuntimeManager = RuntimeManager
core_mod.RI = RI


# Minimal SQL manager mock
sql_manager_mod = types.ModuleType('libs.sql.sql_manager')


class MockSQL:
    def __init__(self):
        self._table_columns = {'Connections': [
            'id', 'token', 'expiration_date'], 'Accounts': ['id', 'email']}
        self.insert_return = 0
        self.update_return = 0
        self.remove_return = 0
        self.get_data_map = {}

    def get_table_column_names(self, table):
        return self._table_columns.get(table, [])

    def insert_or_update_data_into_table(self, table, data, columns):
        return self.insert_return

    def get_data_from_table(self, table, column, where=None, beautify=True):
        # allow simple lookup by where string
        print(
            f"MockSQL.get_data_from_table called: table={table}, column={column}, where={where}")
        if where and "email='" in where:
            # return sample id
            print('MockSQL: returning id row for email')
            return [['1']]
        if where and "token=" in where:
            # only simulate a login row for the known test token 'sometoken' or
            # other tokens used in tests when the token is passed without
            # surrounding quotes (used by is_token_correct). Keep the
            # sentinel behaviour when tokens are quoted (used by generate_token
            # uniqueness checks) to avoid infinite loops.
            if "sometoken" in where or "'good'" in where or "=good" in where or "'" not in where:
                return [[1, 'sometoken', datetime.now() + timedelta(seconds=3600)]]
            # otherwise return an integer sentinel (not found)
            return self.get_data_map.get((table, column, where), 84)
        print('MockSQL: default path, returning map/default')
        return self.get_data_map.get((table, column, where), 84)

    def datetime_to_string(self, datetime_instance, date_only=False, sql_mode=False):
        if isinstance(datetime_instance, (datetime,)):
            return datetime_instance.isoformat()
        return str(datetime_instance)

    def remove_data_from_table(self, table, where):
        return self.remove_return

    def update_data_in_table(self, table, data, column, where):
        return self.update_return


sql_manager_mod.SQL = MockSQL
_sys.modules['libs.sql.sql_manager'] = sql_manager_mod
_sys.modules['src.libs.sql.sql_manager'] = sql_manager_mod


# Make top-level 'libs.sql' package reference available (so 'from ..sql import SQL' works)
sql_pkg = types.ModuleType('libs.sql')
sql_pkg.SQL = MockSQL
_sys.modules['libs.sql'] = sql_pkg
_sys.modules['src.libs.sql'] = sql_pkg

# Load only the boilerplates modules directly to avoid importing the full 'libs' package
boilerplates_dir = src_dir / 'libs' / 'boilerplates'

# Create package placeholders for `src` and `src.libs` so imports like
# `from src.libs.boilerplates import ...` resolve without executing
# the real package __init__.py (which pulls many dependencies).
_sys.modules.setdefault('src', types.ModuleType('src'))
_sys.modules['src'].__path__ = [str(src_dir)]
_sys.modules.setdefault('src.libs', types.ModuleType('src.libs'))
_sys.modules['src.libs'].__path__ = [str(src_dir / 'libs')]
_sys.modules.setdefault('src.libs.boilerplates',
                        types.ModuleType('src.libs.boilerplates'))
_sys.modules['src.libs.boilerplates'].__path__ = [str(boilerplates_dir)]

# Keep legacy `libs` placeholders too (some modules import `libs.*` directly)
_sys.modules.setdefault('libs', types.ModuleType('libs'))
_sys.modules['libs'].__path__ = [str(src_dir / 'libs')]
_sys.modules.setdefault('libs.boilerplates',
                        types.ModuleType('libs.boilerplates'))
_sys.modules['libs.boilerplates'].__path__ = [str(boilerplates_dir)]

# Ensure the package paths exist on sys.modules so normal imports succeed.
_sys.modules.setdefault('src', types.ModuleType('src'))
_sys.modules['src'].__path__ = [str(backend_dir / 'src')]
_sys.modules.setdefault('src.libs', types.ModuleType('src.libs'))
_sys.modules['src.libs'].__path__ = [str(src_dir / 'libs')]
_sys.modules.setdefault('libs', types.ModuleType('libs'))
_sys.modules['libs'].__path__ = [str(src_dir / 'libs')]

# Load each boilerplate module directly from its source file. We execute the
# module with an explicit package context so internal relative imports work.
# Pre-seed the boilerplates package with placeholders for all expected
# exported class names so import-time `from ..boilerplates import X` from
# other modules (like `oauth_authentication`) succeed during circular
# import resolution while we load individual submodules.
pkg_src = _sys.modules.setdefault(
    'src.libs.boilerplates', types.ModuleType('src.libs.boilerplates'))
pkg_src.__path__ = [str(boilerplates_dir)]
pkg_libs = _sys.modules.setdefault(
    'libs.boilerplates', types.ModuleType('libs.boilerplates'))
pkg_libs.__path__ = [str(boilerplates_dir)]
for name in ('BoilerplateIncoming', 'BoilerplateNonHTTP', 'BoilerplateResponses'):
    placeholder = type(f'{name}Placeholder', (), {})
    setattr(pkg_src, name, placeholder)
    setattr(pkg_libs, name, placeholder)
for fname, alias in (('incoming.py', 'test_boiler_incoming'),
                     ('non_web.py', 'test_boiler_non_web'),
                     ('responses.py', 'test_boiler_responses')):
    fpath = boilerplates_dir / fname
    if not fpath.exists():
        raise ImportError(f"Missing boilerplate source file: {fpath}")

    module_name_src = f'src.libs.boilerplates.{fname[:-3]}'
    module_name_libs = f'libs.boilerplates.{fname[:-3]}'

    # Prefer loading into the src.* namespace
    spec = importlib.util.spec_from_file_location(module_name_src, str(fpath))
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot create import spec for {fpath}')

    mod = importlib.util.module_from_spec(spec)
    # ensure package context is set so relative imports inside the module work
    mod.__package__ = 'src.libs.boilerplates'

    # ensure package object exists in sys.modules for relative imports
    pkg_src = _sys.modules.setdefault(
        'src.libs.boilerplates', types.ModuleType('src.libs.boilerplates'))
    pkg_src.__path__ = [str(boilerplates_dir)]
    pkg_libs = _sys.modules.setdefault(
        'libs.boilerplates', types.ModuleType('libs.boilerplates'))
    pkg_libs.__path__ = [str(boilerplates_dir)]

    # Pre-seed the package exports with lightweight placeholders for the
    # expected class names so import-time `from ..boilerplates import X`
    # succeeds during circular imports. These will be replaced after the
    # module is executed with the real class objects.
    exported_name = None
    if fname == 'incoming.py':
        exported_name = 'BoilerplateIncoming'
    elif fname == 'non_web.py':
        exported_name = 'BoilerplateNonHTTP'
    elif fname == 'responses.py':
        exported_name = 'BoilerplateResponses'

    if exported_name is not None:
        placeholder = type(f'{exported_name}Placeholder', (), {})
        setattr(pkg_src, exported_name, placeholder)
        setattr(pkg_libs, exported_name, placeholder)

    _sys.modules[module_name_src] = mod
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    except Exception:
        # Clean up on failure and surface the original exception
        _sys.modules.pop(module_name_src, None)
        # remove placeholders if they were set
        if exported_name is not None:
            for p in ('src.libs.boilerplates', 'libs.boilerplates'):
                pkg = _sys.modules.get(p)
                if pkg is not None and hasattr(pkg, exported_name):
                    delattr(pkg, exported_name)
        raise

    # If the module provided the real exported class, update package attrs
    if exported_name is not None and hasattr(mod, exported_name):
        real = getattr(mod, exported_name)
        setattr(pkg_src, exported_name, real)
        setattr(pkg_libs, exported_name, real)

    # register the same module object under the legacy `libs.*` name so
    # imports using either namespace resolve to the same module object.
    _sys.modules[module_name_libs] = mod
    # create short test alias pointing to the loaded module
    _sys.modules[alias] = mod

# Expose class names at package level to satisfy `from ..boilerplates import ...`
for pkg_name in ('libs.boilerplates', 'src.libs.boilerplates'):
    pkg = _sys.modules.get(pkg_name)
    if pkg is None:
        continue
    inc = _sys.modules.get(f'{pkg_name}.incoming')
    non = _sys.modules.get(f'{pkg_name}.non_web')
    res = _sys.modules.get(f'{pkg_name}.responses')
    if inc is not None and hasattr(inc, 'BoilerplateIncoming'):
        setattr(pkg, 'BoilerplateIncoming',
                getattr(inc, 'BoilerplateIncoming'))
    if non is not None and hasattr(non, 'BoilerplateNonHTTP'):
        setattr(pkg, 'BoilerplateNonHTTP', getattr(non, 'BoilerplateNonHTTP'))
    if res is not None and hasattr(res, 'BoilerplateResponses'):
        setattr(pkg, 'BoilerplateResponses',
                getattr(res, 'BoilerplateResponses'))
# Create short test aliases pointing to the loaded modules (prefer src namespace)
alias_map = {
    'test_boiler_incoming': ('src.libs.boilerplates.incoming', 'libs.boilerplates.incoming'),
    'test_boiler_non_web': ('src.libs.boilerplates.non_web', 'libs.boilerplates.non_web'),
    'test_boiler_responses': ('src.libs.boilerplates.responses', 'libs.boilerplates.responses'),
}
for alias, candidates in alias_map.items():
    for candidate in candidates:
        mod = _sys.modules.get(candidate)
        if mod is not None:
            _sys.modules[alias] = mod
            break
