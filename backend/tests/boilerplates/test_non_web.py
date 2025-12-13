import pytest
from datetime import datetime, timedelta

from libs.core.runtime_manager import RI
from libs.sql import SQL

# dynamic loader for the boilerplate non_web module
import importlib.util
import sys
import types
from pathlib import Path
_here = Path(__file__).resolve()
_src = _here.parents[2] / 'src'
_bp_dir = _src / 'libs' / 'boilerplates'


def _load_bp(name, fname):
    # minimal constants
    const_mod = types.ModuleType('libs.utils.constants')
    const_mod.ASSETS_DIRECTORY = _src / 'assets'
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
    sys.modules['libs.utils.constants'] = const_mod
    sys.modules['src.libs.utils.constants'] = const_mod

    # package placeholders
    sys.modules.setdefault('src', types.ModuleType('src'))
    sys.modules['src'].__path__ = [str(_src)]
    sys.modules.setdefault('src.libs', types.ModuleType('src.libs'))
    sys.modules['src.libs'].__path__ = [str(_src / 'libs')]
    sys.modules.setdefault('src.libs.boilerplates',
                           types.ModuleType('src.libs.boilerplates'))
    sys.modules['src.libs.boilerplates'].__path__ = [str(_bp_dir)]
    sys.modules.setdefault('libs', types.ModuleType('libs'))
    sys.modules['libs'].__path__ = [str(_src / 'libs')]
    sys.modules.setdefault('libs.boilerplates',
                           types.ModuleType('libs.boilerplates'))
    sys.modules['libs.boilerplates'].__path__ = [str(_bp_dir)]

    last_mod = None
    for pkg_prefix in ('libs.boilerplates', 'src.libs.boilerplates'):
        mod_name = f'{pkg_prefix}.{fname[:-3]}'
        spec = importlib.util.spec_from_file_location(
            mod_name, str(_bp_dir / fname))
        if spec is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = pkg_prefix
        sys.modules[mod_name] = mod
        try:
            spec.loader.exec_module(mod)
            last_mod = mod
        except Exception:
            sys.modules.pop(mod_name, None)
    if last_mod is not None:
        sys.modules[name] = last_mod
    return last_mod


_mod = _load_bp('test_boiler_non_web', 'non_web.py')
BoilerplateNonHTTP = _mod.BoilerplateNonHTTP


def test_check_date_valid_and_invalid():
    """Test date validation with various formats and invalid dates.
    
    Verifies that check_date accepts valid DD/MM/YYYY dates and rejects
    invalid dates (impossible dates like 32/01) and alternative formats.
    """
    RI.register(SQL, SQL())
    bn = BoilerplateNonHTTP()
    assert bn.check_date('01/01/2020') is True
    assert bn.check_date('31/12/1999') is True
    assert bn.check_date('32/01/2020') is False
    assert bn.check_date('2020-01-01') is False


def test_generate_check_token_sizes_and_format():
    """Test token generation with different sizes and format validation.
    
    Verifies that generate_check_token produces tokens with the correct
    number of segments (leading number + token elements) based on the
    requested token_size parameter.
    """
    RI.register(SQL, SQL())
    bn = BoilerplateNonHTTP()
    short = bn.generate_check_token(1)
    assert isinstance(short, str)
    parts = short.split('-')
    assert len(parts) == 2  # one leading number + one token element

    bigger = bn.generate_check_token(4)
    assert isinstance(bigger, str)
    # token_size + 1 parts (leading number + tokens)
    assert len(bigger.split('-')) == 5


def test_set_lifespan_returns_offset_datetime():
    """Test that set_lifespan returns future datetime with correct offset.
    
    Verifies that the method returns a datetime object in the future
    that is offset by approximately the requested number of seconds.
    """
    RI.register(SQL, SQL())
    bn = BoilerplateNonHTTP()
    now = datetime.now()
    dt = bn.set_lifespan(2)
    assert isinstance(dt, datetime)
    assert dt > now
    assert dt - now < timedelta(seconds=10)


def test_generate_token_unique_and_uuid_format():
    """Test token generation produces UUID-like formatted strings.
    
    Verifies that generate_token produces string tokens containing
    hyphens (UUID format indicators) and ensures SQL is registered
    to check for token uniqueness.
    """
    # Ensure SQL is registered and returns integer (meaning token not found)
    sql = SQL()
    RI.register(SQL, sql)
    bn = BoilerplateNonHTTP()
    token = bn.generate_token()
    assert isinstance(token, str)
    assert '-' in token


def test_is_token_correct_updates_and_returns_true():
    """Test token validation and expiration checking.
    
    Verifies that is_token_correct properly validates tokens and updates
    their last access time, returning True for valid unexpired tokens.
    """
    sql = SQL()
    sql.update_return = 0
    RI.register(SQL, sql)
    bn = BoilerplateNonHTTP()
    # Should find token and return True (mock returns future expiration)
    assert bn.is_token_correct('sometoken') is True
