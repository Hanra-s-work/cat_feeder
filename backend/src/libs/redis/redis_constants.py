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
# FILE: redis_constants.py
# CREATION DATE: 17-11-2025
# LAST Modified: 15:34:26 17-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: These are the constants for the redis class that will allow the class to have descriptive info.
# // AR
# +==== END AsperBackend =================+
"""

# DEFAULT environement variables
REDIS_SOCKET_KEY: str = "REDIS_SOCKET"
REDIS_PASSWORD_KEY: str = "REDIS_PASSWORD"
REDIS_SOCKET_DEFAULT: str = "/run/redis/redis.sock"

# Seconds
SEC_1: int = 1
SEC_2: int = SEC_1*2
SEC_3: int = SEC_1*3
SEC_4: int = SEC_1*4
SEC_5: int = SEC_1*5
SEC_6: int = SEC_1*6
SEC_7: int = SEC_1*7
SEC_8: int = SEC_1*8
SEC_9: int = SEC_1*9
SEC_10: int = SEC_1*10
SEC_11: int = SEC_1*11
SEC_12: int = SEC_1*12
SEC_13: int = SEC_1*13
SEC_14: int = SEC_1*14
SEC_15: int = SEC_1*15
SEC_16: int = SEC_1*16
SEC_17: int = SEC_1*17
SEC_18: int = SEC_1*18
SEC_19: int = SEC_1*19
SEC_20: int = SEC_1*20
SEC_21: int = SEC_1*21
SEC_22: int = SEC_1*22
SEC_23: int = SEC_1*23
SEC_24: int = SEC_1*24
SEC_25: int = SEC_1*25
SEC_26: int = SEC_1*26
SEC_27: int = SEC_1*27
SEC_28: int = SEC_1*28
SEC_29: int = SEC_1*29
SEC_30: int = SEC_1*30
SEC_31: int = SEC_1*31
SEC_32: int = SEC_1*32
SEC_33: int = SEC_1*33
SEC_34: int = SEC_1*34
SEC_35: int = SEC_1*35
SEC_36: int = SEC_1*36
SEC_37: int = SEC_1*37
SEC_38: int = SEC_1*38
SEC_39: int = SEC_1*39
SEC_40: int = SEC_1*40
SEC_41: int = SEC_1*41
SEC_42: int = SEC_1*42
SEC_43: int = SEC_1*43
SEC_44: int = SEC_1*44
SEC_45: int = SEC_1*45
SEC_46: int = SEC_1*46
SEC_47: int = SEC_1*47
SEC_48: int = SEC_1*48
SEC_49: int = SEC_1*49
SEC_50: int = SEC_1*50
SEC_51: int = SEC_1*51
SEC_52: int = SEC_1*52
SEC_53: int = SEC_1*53
SEC_54: int = SEC_1*54
SEC_55: int = SEC_1*55
SEC_56: int = SEC_1*56
SEC_57: int = SEC_1*57
SEC_58: int = SEC_1*58
SEC_59: int = SEC_1*59
SEC_60: int = SEC_1*60

# Minutes
MIN_1: int = SEC_1*60
MIN_2: int = MIN_1*2
MIN_3: int = MIN_1*3
MIN_4: int = MIN_1*4
MIN_5: int = MIN_1*5
MIN_6: int = MIN_1*6
MIN_7: int = MIN_1*7
MIN_8: int = MIN_1*8
MIN_9: int = MIN_1*9
MIN_10: int = MIN_1*10
MIN_11: int = MIN_1*11
MIN_12: int = MIN_1*12
MIN_13: int = MIN_1*13
MIN_14: int = MIN_1*14
MIN_15: int = MIN_1*15
MIN_16: int = MIN_1*16
MIN_17: int = MIN_1*17
MIN_18: int = MIN_1*18
MIN_19: int = MIN_1*19
MIN_20: int = MIN_1*20
MIN_21: int = MIN_1*21
MIN_22: int = MIN_1*22
MIN_23: int = MIN_1*23
MIN_24: int = MIN_1*24
MIN_25: int = MIN_1*25
MIN_26: int = MIN_1*26
MIN_27: int = MIN_1*27
MIN_28: int = MIN_1*28
MIN_29: int = MIN_1*29
MIN_30: int = MIN_1*30
MIN_31: int = MIN_1*31
MIN_32: int = MIN_1*32
MIN_33: int = MIN_1*33
MIN_34: int = MIN_1*34
MIN_35: int = MIN_1*35
MIN_36: int = MIN_1*36
MIN_37: int = MIN_1*37
MIN_38: int = MIN_1*38
MIN_39: int = MIN_1*39
MIN_40: int = MIN_1*40
MIN_41: int = MIN_1*41
MIN_42: int = MIN_1*42
MIN_43: int = MIN_1*43
MIN_44: int = MIN_1*44
MIN_45: int = MIN_1*45
MIN_46: int = MIN_1*46
MIN_47: int = MIN_1*47
MIN_48: int = MIN_1*48
MIN_49: int = MIN_1*49
MIN_50: int = MIN_1*50
MIN_51: int = MIN_1*51
MIN_52: int = MIN_1*52
MIN_53: int = MIN_1*53
MIN_54: int = MIN_1*54
MIN_55: int = MIN_1*55
MIN_56: int = MIN_1*56
MIN_57: int = MIN_1*57
MIN_58: int = MIN_1*58
MIN_59: int = MIN_1*59
MIN_60: int = MIN_1*60

# Hours
HOUR_1: int = MIN_1*60
HOUR_2: int = HOUR_1*2
HOUR_3: int = HOUR_1*3
HOUR_4: int = HOUR_1*4
HOUR_5: int = HOUR_1*5
HOUR_6: int = HOUR_1*6
HOUR_7: int = HOUR_1*7
HOUR_8: int = HOUR_1*8
HOUR_9: int = HOUR_1*9
HOUR_10: int = HOUR_1*10
HOUR_11: int = HOUR_1*11
HOUR_12: int = HOUR_1*12
HOUR_13: int = HOUR_1*13
HOUR_14: int = HOUR_1*14
HOUR_15: int = HOUR_1*15
HOUR_16: int = HOUR_1*16
HOUR_17: int = HOUR_1*17
HOUR_18: int = HOUR_1*18
HOUR_19: int = HOUR_1*19
HOUR_20: int = HOUR_1*20
HOUR_21: int = HOUR_1*21
HOUR_22: int = HOUR_1*22
HOUR_23: int = HOUR_1*23
HOUR_24: int = HOUR_1*24

# Days
DAY_1: int = HOUR_24
DAY_2: int = DAY_1*2
DAY_3: int = DAY_1*3
DAY_4: int = DAY_1*4
DAY_5: int = DAY_1*5
DAY_6: int = DAY_1*6
DAY_7: int = DAY_1*7

# Weeks
WEEK_1: int = DAY_7
WEEK_2: int = WEEK_1*2
WEEK_3: int = WEEK_1*3
WEEK_4: int = WEEK_1*4

# Years
YEAR_1: int = DAY_1 * 365
