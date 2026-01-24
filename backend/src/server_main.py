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
# FILE: server_main.py
# CREATION DATE: 11-10-2025
# LAST Modified: 22:21:9 14-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file allowing the server to be run as a standalone.
# // AR
# +==== END CatFeeder =================+
"""


import sys
from sys import argv

try:
    from .libs import Server, CONST, FinalClass
except ImportError:
    from libs import Server, CONST, FinalClass


class Main(metaclass=FinalClass):
    """_summary_
    This class is a bootstrapper for launching the server in standalone mode.
    """

    def __init__(self, success: int = 0, error: int = 84) -> None:
        self.argc = len(argv)
        self.host: str = "0.0.0.0"
        self.port: int = 5000
        self.success: int = success
        self.error: int = error
        self.app_name: str = "Asperguide"
        self.debug: bool = False or CONST.DEBUG

    def process_args(self) -> None:
        """_summary_
        Check the arguments that are input (if any)
        """
        i = 1
        while i < self.argc:
            arg = argv[i].lower()
            if "--help" in arg or "-h" == arg:
                print("Usage: python3 ./server [OPTIONS]")
                print("Options:")
                print(
                    "  --host=<host>                                                       The host to bind the server to (default: '0.0.0.0')"
                )
                print(
                    "  --port=<port>, -p <port>                                            The port to bind the server to (default: 5000)"
                )
                print(
                    "  --success=<number>, -s <number>                                     Change the success exit code (default: 0)"
                )
                print(
                    "  --error=<number>, -e <number>                                       Change the error exit code (default: 1)"
                )
                print(
                    "  --debug                                                             Enable debug mode"
                )
                print(
                    "  --config                                                            Specify the configuration file to load when the server is started (default: config.toml)"
                )
                print(
                    "  --env                                                               Specify the environement file to load when the server is started (default: .env)"
                )
                print(
                    "  --help, -h                                                          Show this help message"
                )
                sys.exit(self.success)
            elif "--host" in arg:
                if '=' in arg:
                    self.host = arg.split("=")[1]
                else:
                    if i+1 < self.argc:
                        self.host = argv[i + 1]
                        i += 1
            elif "--port" in arg or '-p' in arg:
                if '=' in arg:
                    self.port = int(arg.split("=")[1])
                else:
                    if i+1 < self.argc:
                        self.port = int(argv[i + 1])
                        i += 1
            elif "--success" in arg or "-s" in arg:
                if '=' in arg:
                    self.success = int(arg.split("=")[1])
                else:
                    if i+1 < self.argc:
                        self.success = int(argv[i + 1])
                        i += 1
            elif "--error" in arg or "-e" in arg:
                if '=' in arg:
                    self.error = int(arg.split("=")[1])
                else:
                    if i+1 < self.argc:
                        self.error = int(argv[i + 1])
                        i += 1
            elif "--debug" in arg or "-d" in arg:
                self.debug = True

            else:
                print(f"Unknown argument: {arg}")
            i += 1

    def main(self) -> None:
        """_summary_
        This method is the entry point of the server.
        """
        if self.argc > 1:
            self.process_args()
            SI = Server(
                host=self.host,
                port=self.port,
                success=self.success,
                error=self.error,
                app_name=self.app_name,
                debug=self.debug
            )
            try:
                status = SI.main()
            except KeyboardInterrupt:
                print("\nCtrl+C caught! Exiting the program gracefully.")
                del SI
                status = self.success
            except RuntimeError as e:
                print(
                    f"A potentially handled error has forced the server to stop: {e}")
                status = self.error
            except Exception as e:
                print(f"An error occurred: {e}")
                raise RuntimeError(
                    "The server is exiting with a fatal failure"
                ) from e
            print(f"The server is exiting with a status of: {status}")
            sys.exit(status)

        else:
            print(f"Usage: python3 {sys.argv[0]} --help")
            sys.exit(self.success)


if __name__ == "__main__":
    MI = Main(
        success=CONST.SUCCESS,
        error=CONST.ERROR
    )
    MI.main()
