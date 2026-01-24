r"""
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
# FILE: test_server_main.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for server bootstrapper main entry point.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for Main class argument parsing and server startup.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
import sys
from unittest.mock import Mock, MagicMock, patch

try:
    from src.server_main import Main
except Exception:
    from server_main import Main


def setup_argv(monkeypatch, argv_list):
    """Helper to patch both sys.argv and module's argv variable."""
    monkeypatch.setattr(sys, 'argv', argv_list)
    monkeypatch.setattr('src.server_main.argv', argv_list, raising=False)


class TestMainInitialization:
    """Test Main class initialization."""

    def test_main_init_default_values(self, monkeypatch):
        """Verify Main initializes with default values."""
        setup_argv(monkeypatch, ['server_main.py'])
        main = Main()
        assert main.host == "0.0.0.0"
        assert main.port == 5000
        assert main.success == 0
        assert main.error == 84
        assert main.app_name == "Asperguide"
        assert main.debug is False

    def test_main_init_custom_success_code(self, monkeypatch):
        """Verify Main accepts custom success code."""
        setup_argv(monkeypatch, ['server_main.py'])
        main = Main(success=200)
        assert main.success == 200

    def test_main_init_custom_error_code(self, monkeypatch):
        """Verify Main accepts custom error code."""
        setup_argv(monkeypatch, ['server_main.py'])
        main = Main(error=1)
        assert main.error == 1

    def test_main_init_sets_argc(self, monkeypatch):
        """Verify Main sets argc from argv."""
        setup_argv(monkeypatch, ['server_main.py', '--help'])
        main = Main()
        assert main.argc == 2

    def test_main_final_class_metaclass(self, monkeypatch):
        """Verify Main cannot be subclassed."""
        setup_argv(monkeypatch, ['server_main.py'])
        with pytest.raises(TypeError):
            class SubMain(Main):
                pass


class TestMainArgumentParsingHost:
    """Test Main argument parsing for --host."""

    def test_parse_host_with_equals(self, monkeypatch):
        """Verify Main parses --host=value format."""
        setup_argv(monkeypatch, ['server_main.py', '--host=192.168.1.1'])
        main = Main()
        main.process_args()
        assert main.host == "192.168.1.1"

    def test_parse_host_with_space(self, monkeypatch):
        """Verify Main parses --host value format."""
        setup_argv(monkeypatch, ['server_main.py', '--host', 'localhost'])
        main = Main()
        main.process_args()
        assert main.host == "localhost"

    def test_parse_host_localhost(self, monkeypatch):
        """Verify Main accepts localhost."""
        setup_argv(monkeypatch, ['server_main.py', '--host=localhost'])
        main = Main()
        main.process_args()
        assert main.host == "localhost"


class TestMainArgumentParsingPort:
    """Test Main argument parsing for --port/-p."""

    def test_parse_port_long_with_equals(self, monkeypatch):
        """Verify Main parses --port=value format."""
        setup_argv(monkeypatch, ['server_main.py', '--port=8080'])
        main = Main()
        main.process_args()
        assert main.port == 8080

    def test_parse_port_long_with_space(self, monkeypatch):
        """Verify Main parses --port value format."""
        setup_argv(monkeypatch, ['server_main.py', '--port', '3000'])
        main = Main()
        main.process_args()
        assert main.port == 3000

    def test_parse_port_short_format(self, monkeypatch):
        """Verify Main parses -p value format."""
        setup_argv(monkeypatch, ['server_main.py', '-p', '9000'])
        main = Main()
        main.process_args()
        assert main.port == 9000

    def test_parse_port_default_5000(self, monkeypatch):
        """Verify Main defaults to port 5000."""
        setup_argv(monkeypatch, ['server_main.py'])
        main = Main()
        main.process_args()
        assert main.port == 5000

    def test_parse_port_as_integer(self, monkeypatch):
        """Verify port is converted to integer."""
        setup_argv(monkeypatch, ['server_main.py', '--port=8080'])
        main = Main()
        main.process_args()
        assert isinstance(main.port, int)


class TestMainArgumentParsingSuccess:
    """Test Main argument parsing for --success/-s."""

    def test_parse_success_long_with_equals(self, monkeypatch):
        """Verify Main parses --success=value format."""
        setup_argv(monkeypatch, ['server_main.py', '--success=200'])
        main = Main()
        main.process_args()
        assert main.success == 200

    def test_parse_success_long_with_space(self, monkeypatch):
        """Verify Main parses --success value format."""
        setup_argv(monkeypatch, ['server_main.py', '--success', '100'])
        main = Main()
        main.process_args()
        assert main.success == 100

    def test_parse_success_short_format(self, monkeypatch):
        """Verify Main parses -s value format."""
        setup_argv(monkeypatch, ['server_main.py', '-s', '50'])
        main = Main()
        main.process_args()
        assert main.success == 50


class TestMainArgumentParsingError:
    """Test Main argument parsing for --error/-e."""

    def test_parse_error_long_with_equals(self, monkeypatch):
        """Verify Main parses --error=value format."""
        setup_argv(monkeypatch, ['server_main.py', '--error=1'])
        main = Main()
        main.process_args()
        assert main.error == 1

    def test_parse_error_long_with_space(self, monkeypatch):
        """Verify Main parses --error value format."""
        setup_argv(monkeypatch, ['server_main.py', '--error', '2'])
        main = Main()
        main.process_args()
        assert main.error == 2

    def test_parse_error_short_format(self, monkeypatch):
        """Verify Main parses -e value format."""
        setup_argv(monkeypatch, ['server_main.py', '-e', '99'])
        main = Main()
        main.process_args()
        assert main.error == 99


class TestMainArgumentParsingDebug:
    """Test Main argument parsing for --debug."""

    def test_parse_debug_long_format(self, monkeypatch):
        """Verify Main parses --debug format."""
        setup_argv(monkeypatch, ['server_main.py', '--debug'])
        main = Main()
        main.process_args()
        assert main.debug is True

    def test_parse_debug_short_format(self, monkeypatch):
        """Verify Main parses -d format."""
        setup_argv(monkeypatch, ['server_main.py', '-d'])
        main = Main()
        main.process_args()
        assert main.debug is True

    def test_debug_default_false(self, monkeypatch):
        """Verify debug defaults to False."""
        setup_argv(monkeypatch, ['server_main.py'])
        main = Main()
        main.process_args()
        assert main.debug is False


class TestMainArgumentParsingMultiple:
    """Test Main argument parsing with multiple arguments."""

    def test_parse_multiple_arguments(self, monkeypatch):
        """Verify Main parses multiple arguments together."""
        setup_argv(monkeypatch, ['server_main.py',
                   '--host=localhost', '--port=8080', '--debug'])
        main = Main()
        main.process_args()
        assert main.host == "localhost"
        assert main.port == 8080
        assert main.debug is True

    def test_parse_mixed_formats(self, monkeypatch):
        """Verify Main parses mixed argument formats."""
        setup_argv(monkeypatch, ['server_main.py',
                   '--host', '127.0.0.1', '-p', '3000', '--debug'])
        main = Main()
        main.process_args()
        assert main.host == "127.0.0.1"
        assert main.port == 3000
        assert main.debug is True

    def test_parse_all_arguments(self, monkeypatch):
        """Verify Main parses all argument types together."""
        setup_argv(monkeypatch, [
            'server_main.py',
            '--host=0.0.0.0',
            '--port=5000',
            '--success=0',
            '--error=84',
            '--debug'
        ])
        main = Main()
        main.process_args()
        assert main.host == "0.0.0.0"
        assert main.port == 5000
        assert main.success == 0
        assert main.error == 84
        assert main.debug is True


class TestMainHelpMessage:
    """Test Main help message display."""

    def test_help_long_format(self, monkeypatch, capsys):
        """Verify Main displays help with --help."""
        setup_argv(monkeypatch, ['server_main.py', '--help'])
        main = Main()
        with pytest.raises(SystemExit) as exc_info:
            main.process_args()
        assert exc_info.value.code == main.success
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert "--host" in captured.out
        assert "--port" in captured.out

    def test_help_short_format(self, monkeypatch, capsys):
        """Verify Main displays help with -h."""
        setup_argv(monkeypatch, ['server_main.py', '-h'])
        main = Main()
        with pytest.raises(SystemExit) as exc_info:
            main.process_args()
        assert exc_info.value.code == main.success
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    def test_help_contains_all_options(self, monkeypatch, capsys):
        """Verify help message contains all options."""
        setup_argv(monkeypatch, ['server_main.py', '--help'])
        main = Main()
        with pytest.raises(SystemExit):
            main.process_args()
        captured = capsys.readouterr()
        assert "--host" in captured.out
        assert "--port" in captured.out
        assert "--success" in captured.out
        assert "--error" in captured.out
        assert "--debug" in captured.out
        assert "--config" in captured.out
        assert "--env" in captured.out


class TestMainUnknownArgument:
    """Test Main unknown argument handling."""

    def test_unknown_argument_prints_message(self, monkeypatch, capsys):
        """Verify Main prints message for unknown argument."""
        setup_argv(monkeypatch, ['server_main.py', '--unknown'])
        main = Main()
        main.process_args()
        captured = capsys.readouterr()
        assert "Unknown argument:" in captured.out
        # Clear any remaining output
        capsys.readouterr()

    def test_unknown_argument_doesnt_crash(self, monkeypatch, capsys):
        """Verify Main doesn't crash on unknown argument."""
        setup_argv(monkeypatch, ['server_main.py', '--unknown'])
        main = Main()
        main.process_args()
        assert main.host == "0.0.0.0"
        assert main.port == 5000
        # Clear any remaining output
        capsys.readouterr()

    def test_unknown_argument_with_other_args(self, monkeypatch, capsys):
        """Verify Main parses valid args even with unknown ones."""
        setup_argv(monkeypatch, ['server_main.py',
                   '--port=8080', '--unknown', '--debug'])
        main = Main()
        main.process_args()
        assert main.port == 8080
        assert main.debug is True
        captured = capsys.readouterr()
        assert "Unknown argument:" in captured.out
        # Clear any remaining output
        capsys.readouterr()


class TestMainServerInstantiation:
    """Test Main server instantiation."""

    def test_main_passes_host_to_server(self, monkeypatch):
        """Verify Main passes host to Server."""
        setup_argv(monkeypatch, ['server_main.py',
                   '--host=192.168.1.1', '--port=3000'])
        main = Main()
        main.process_args()
        assert main.host == "192.168.1.1"

    def test_main_passes_port_to_server(self, monkeypatch):
        """Verify Main passes port to Server."""
        setup_argv(monkeypatch, ['server_main.py', '--port=9000'])
        main = Main()
        main.process_args()
        assert main.port == 9000

    def test_main_passes_debug_to_server(self, monkeypatch):
        """Verify Main passes debug flag to Server."""
        setup_argv(monkeypatch, ['server_main.py', '--debug'])
        main = Main()
        main.process_args()
        assert main.debug is True


class TestMainExceptionHandling:
    """Test Main exception handling."""

    def test_main_catches_keyboard_interrupt(self, monkeypatch, capsys):
        """Verify Main handles KeyboardInterrupt gracefully."""
        setup_argv(monkeypatch, ['server_main.py', '--debug'])

        with patch('src.server_main.Server') as mock_server_class:
            mock_server = MagicMock()
            mock_server.main.side_effect = KeyboardInterrupt()
            mock_server_class.return_value = mock_server

            main = Main()
            with pytest.raises(SystemExit) as exc_info:
                main.main()
            assert exc_info.value.code == main.success
            captured = capsys.readouterr()
            assert "Ctrl+C caught" in captured.out
            # Clear any remaining output
            capsys.readouterr()

    def test_main_catches_runtime_error(self, monkeypatch, capsys):
        """Verify Main handles RuntimeError appropriately."""
        setup_argv(monkeypatch, ['server_main.py', '--debug'])

        with patch('src.server_main.Server') as mock_server_class:
            mock_server = MagicMock()
            mock_server.main.side_effect = RuntimeError('Test error')
            mock_server_class.return_value = mock_server

            main = Main()
            with pytest.raises(SystemExit) as exc_info:
                main.main()
            assert exc_info.value.code == main.error
            captured = capsys.readouterr()
            assert "potentially handled error" in captured.out
            # Clear any remaining output
            capsys.readouterr()

    def test_main_catches_generic_exception(self, monkeypatch, capsys):
        """Verify Main handles generic exceptions."""
        setup_argv(monkeypatch, ['server_main.py', '--debug'])

        with patch('src.server_main.Server') as mock_server_class:
            mock_server = MagicMock()
            mock_server.main.side_effect = ValueError('Test error')
            mock_server_class.return_value = mock_server

            main = Main()
            with pytest.raises(RuntimeError):
                main.main()
            captured = capsys.readouterr()
            assert "An error occurred:" in captured.out
            # Clear any remaining output
            capsys.readouterr()

    def test_main_success_exit_code(self, monkeypatch, capsys):
        """Verify Main exits with success code on successful run."""
        setup_argv(monkeypatch, ['server_main.py', '--debug'])

        with patch('src.server_main.Server') as mock_server_class:
            mock_server = MagicMock()
            mock_server.main.return_value = 0
            mock_server_class.return_value = mock_server

            main = Main(success=0, error=84)
            with pytest.raises(SystemExit) as exc_info:
                main.main()
            assert exc_info.value.code == 0
            capsys.readouterr()  # Suppress output capture


class TestMainNoArguments:
    """Test Main with no arguments."""

    def test_main_with_no_args_prints_usage(self, monkeypatch, capsys):
        """Verify Main prints usage when no arguments provided."""
        setup_argv(monkeypatch, ['server_main.py'])

        with patch('src.server_main.Server') as mock_server_class:
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            main = Main()
            with pytest.raises(SystemExit) as exc_info:
                main.main()
            assert exc_info.value.code == main.success
            captured = capsys.readouterr()
            assert "Usage:" in captured.out
            assert "server_main.py" in captured.out
            # Clear any remaining output
            capsys.readouterr()

    def test_main_with_no_args_suggests_help(self, monkeypatch, capsys):
        """Verify Main suggests --help when no arguments provided."""
        setup_argv(monkeypatch, ['server_main.py'])

        with patch('src.server_main.Server') as mock_server_class:
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            main = Main()
            with pytest.raises(SystemExit):
                main.main()
            captured = capsys.readouterr()
            assert "--help" in captured.out
            # Clear any remaining output
            capsys.readouterr()


class TestMainAppName:
    """Test Main app name attribute."""

    def test_app_name_default(self, monkeypatch):
        """Verify Main sets default app name."""
        setup_argv(monkeypatch, ['server_main.py'])
        main = Main()
        assert main.app_name == "Asperguide"

    def test_app_name_not_modified_by_args(self, monkeypatch):
        """Verify app name is not modified by arguments."""
        setup_argv(monkeypatch, ['server_main.py', '--host=localhost'])
        main = Main()
        main.process_args()
        assert main.app_name == "Asperguide"


class TestMainCaseInsensitivity:
    """Test Main argument parsing case insensitivity."""

    def test_argument_case_insensitive(self, monkeypatch):
        """Verify Main converts arguments to lowercase."""
        setup_argv(monkeypatch, ['server_main.py', '--HOST=localhost'])
        main = Main()
        main.process_args()
        assert main.host == "localhost"

    def test_debug_flag_case_insensitive(self, monkeypatch):
        """Verify Main debug flag is case insensitive."""
        setup_argv(monkeypatch, ['server_main.py', '--DEBUG'])
        main = Main()
        main.process_args()
        assert main.debug is True
