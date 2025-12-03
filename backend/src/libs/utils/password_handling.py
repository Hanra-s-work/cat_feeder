""" 
# +==== BEGIN AsperBackend =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: password_handling.py
# CREATION DATE: 11-10-2025
# LAST Modified: 3:54:33 25-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: File containing the class in charge of handling password for the server.
# // AR
# +==== END AsperBackend =================+
"""

import bcrypt
from typing import Union
from display_tty import Disp, initialise_logger


class PasswordHandling:
    """__summary__
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, error: int = 84, success: int = 0, debug: bool = False) -> None:
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.salt_rounds = 10
        self.disp.log_debug("Initialised")

    def hash_password(self, password: Union[str, bytes]) -> str:
        """
            The function to hash the password for the security
        Args:
            password (str): The entered password

        Returns:
            str: The hashed password

        Raises:
            TypeError: if the provided password does not match the expected type.
        """
        title = "_hash_password"
        self.disp.log_debug("Enter hash password", f"{title}")
        if not isinstance(password, (str, bytes)):
            raise TypeError("The password is neither bytes nor a string")
        if isinstance(password, str):
            password = bytes(password, encoding="utf-8")
        self.disp.log_debug("Start register endpoint", f"{title}")
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        safe_password = bcrypt.hashpw(password, salt)
        return safe_password.decode("utf-8")

    def check_password(self, password: Union[str, bytes], password_hash: bytes) -> bool:
        """
            The function to check the entered password with the hashed password
        Args:
            password (str): The entered password
            password_hash (bytes): The hashed password

        Returns:
            bool: True if it's the same, False if not

        Raises:
            TypeError: if the provided password does not match the expected type.
        """
        msg = f"password = {type(password)}, "
        msg += f"password_hash = {type(password_hash)}"
        self.disp.log_debug(msg, "check_password")
        if not isinstance(password, (str, bytes)):
            raise TypeError("The password is neither bytes nor a string")
        if not isinstance(password_hash, (str, bytes)):
            raise TypeError("The password_hash is neither bytes nor a string")
        if isinstance(password, str):
            password = password.encode("utf-8")
        if isinstance(password_hash, str):
            password_hash = password_hash.encode("utf-8")
        msg = f"password = {type(password)}, password_hash = "
        msg += f"{type(password_hash)}"
        self.disp.log_debug(msg, "check_password")
        return bcrypt.checkpw(password, password_hash)
