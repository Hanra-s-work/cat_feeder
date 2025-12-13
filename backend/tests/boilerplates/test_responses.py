from libs.core.runtime_manager import RI
from libs.sql import SQL
from libs.server_header import ServerHeaders

# dynamic loader for boilerplate responses + non_web
import importlib.util
import sys
from pathlib import Path
_here = Path(__file__).resolve()
_src = _here.parents[2] / 'src'
_bp_dir = _src / 'libs' / 'boilerplates'


def _load(name, fname):
    # ensure minimal constants for deeper imports
    import types
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


_mod_res = _load('test_boiler_responses', 'responses.py')
_mod_non = _load('test_boiler_non_web', 'non_web.py')
BoilerplateResponses = _mod_res.BoilerplateResponses
BoilerplateNonHTTP = _mod_non.BoilerplateNonHTTP


def test_build_response_body_logged_in_and_not_logged_in():
    """Test response body construction with logged-in state detection.
    
    Verifies that build_response_body correctly includes title, message,
    resp/error fields, and sets logged_in status based on token validity.
    """
    # register server headers and a boilerplate non-http that returns True
    RI.register(ServerHeaders, ServerHeaders())

    class MockBPNH(BoilerplateNonHTTP):
        """Mock BoilerplateNonHTTP with controlled token validation.
        
        Returns True when validating the token 'good', False otherwise.
        """
        def is_token_correct(self, token: str) -> bool:
            return token == 'good'

    RI.register(BoilerplateNonHTTP, MockBPNH())
    RI.register(SQL, SQL())

    br = BoilerplateResponses()
    body = br.build_response_body(
        't', 'm', {'a': 1}, token='good', error=False)
    assert body['title'] == 't'
    assert body['message'] == 'm'
    assert body['resp'] == {'a': 1}
    assert body['logged_in'] is True

    # token missing
    body2 = br.build_response_body('t2', 'm2', 'x', token=None, error=True)
    assert body2['title'] == 't2'
    assert body2['message'] == 'm2'
    assert body2['error'] == 'x'
    assert body2['logged_in'] is False


def test_response_helpers_return_hci_wrappers():
    """Test that all response helper methods return proper HTTP code identifiers.
    
    Verifies that convenience methods like invalid_token, no_access_token,
    etc. return tuples starting with the appropriate HTTP code identifier
    string that can be used to generate HTTP responses.
    """
    RI.register(ServerHeaders, ServerHeaders())
    RI.register(BoilerplateNonHTTP, BoilerplateNonHTTP())
    RI.register(SQL, SQL())
    br = BoilerplateResponses()
    assert br.invalid_token('t')[0] == 'invalid_token'
    assert br.no_access_token('t')[0] == 'bad_request'
    assert br.provider_not_found('t')[0] == 'not_found'
    assert br.not_logged_in('t')[0] == 'unauthorized'
    assert br.login_failed('t')[0] == 'unauthorized'
    assert br.insuffisant_rights('t')[0] == 'forbidden'
    assert br.bad_request('t')[0] == 'bad_request'
    assert br.internal_server_error('t')[0] == 'internal_server_error'
    assert br.unauthorized('t')[0] == 'unauthorized'
    assert br.user_not_found('t')[0] == 'not_found'
    assert br.invalid_verification_code('t')[0] == 'bad_request'
