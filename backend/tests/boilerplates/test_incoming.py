""" 
# +==== BEGIN CatFeeder =================+
# LOGO: 
# ..............(..../\
# ...............)..(.')
# ..............(../..)
# ...............\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: test_incoming.py
# CREATION DATE: 11-12-2025
# LAST Modified: 2:18:56 11-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of testing the functions from the boilerplate incoming class.
# // AR
# +==== END CatFeeder =================+
"""
import asyncio
import pytest
from datetime import datetime

from src.libs.core.runtime_manager import RI
from src.libs.sql import SQL

# Dynamic loader for boilerplate modules (robust to test runner cwd)
import importlib.util
import sys
import types
from pathlib import Path
_here = Path(__file__).resolve()
_src = _here.parents[2] / 'src'
_bp_dir = _src / 'libs' / 'boilerplates'


def _load_bp(name, fname):
    # provide minimal constants module expected by deeper imports
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

    # Ensure package placeholders exist so relative imports resolve
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

    # load module under both package-qualified names so class identities
    # line up with imports inside the code
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
    # also register the easy alias pointing to the successfully loaded module
    if last_mod is not None:
        sys.modules[name] = last_mod
    return last_mod


_mod_in = _load_bp('test_boiler_incoming', 'incoming.py')
_mod_non = _load_bp('test_boiler_non_web', 'non_web.py')
BoilerplateIncoming = _mod_in.BoilerplateIncoming
BoilerplateNonHTTP = _mod_non.BoilerplateNonHTTP


class FakeRequest:
    def __init__(self, mapping=None, headers=None, json_body=None, form_body=None):
        self._mapping = mapping or {}
        self.headers = headers or {}
        self._json = json_body
        self._form = form_body

    def get(self, key, default=None):
        return self._mapping.get(key, default)

    async def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json

    async def form(self):
        # return a mapping-like object
        return self._form or {}


class MockBPNH(BoilerplateNonHTTP):
    def __init__(self):
        super().__init__()

    def is_token_correct(self, token: str) -> bool:
        return token == 'valid'

    def generate_token(self):
        return 'tok'

    def set_lifespan(self, seconds: int):
        return datetime.now()


def test_get_body_json_and_form():
    RI.register(SQL, SQL())
    bi = BoilerplateIncoming()
    # JSON body
    req = FakeRequest(json_body={'a': 1})
    body = asyncio.run(bi.get_body(req))
    assert body == {'a': 1}

    # form with a file-like object
    class Upload:
        def __init__(self):
            self.filename = 'f'
            self.content_type = 'bin'

        async def read(self):
            return b'bytes'

    form = {'field': 'value', 'file1': Upload()}
    req2 = FakeRequest(json_body=Exception('no json'), form_body=form)
    # ensure the module's UploadFile type matches our Upload class so
    # isinstance checks inside the boilerplate succeed
    try:
        _mod_in.UploadFile = Upload
    except Exception:
        pass
    body2 = asyncio.run(bi.get_body(req2))
    assert '_files' in body2
    assert 'file1' in body2['_files']
    assert body2['_files']['file1']['content'] == b'bytes'


def test_get_token_if_present_variants():
    RI.register(SQL, SQL())
    bi = BoilerplateIncoming()
    # present in headers (mapping-based lookup can vary depending on request wrapper)
    req = FakeRequest(mapping={}, headers={'X-Token': 'm'})
    assert bi.get_token_if_present(req) == 'm'
    # bearer header
    req2 = FakeRequest(mapping={}, headers={'Authorization': 'Bearer abc'})
    assert bi.get_token_if_present(req2) == 'abc'
    # no token
    req3 = FakeRequest(mapping={}, headers={})
    assert bi.get_token_if_present(req3) is None


def test_log_user_in_and_out_flow():
    sql = SQL()
    sql.insert_return = 0
    sql.remove_return = 0
    RI.register(SQL, sql)
    # register a mock BoilerplateNonHTTP that will generate tokens and handle lifespan
    RI.register(BoilerplateNonHTTP, MockBPNH())
    # also register under the class object used by the loaded non_web module
    try:
        RI.register(_mod_non.BoilerplateNonHTTP, MockBPNH())
    except Exception:
        pass
    bi = BoilerplateIncoming()
    res = bi.log_user_in(email='a@b.com')
    assert res['status'] == 0
    assert 'token' in res and res['token'] != ''

    # log out path
    out = bi.log_user_out(token='sometoken')
    assert isinstance(out, dict)
    assert out['status'] == 0
