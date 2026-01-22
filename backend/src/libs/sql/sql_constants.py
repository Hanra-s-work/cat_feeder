"""
# +==== BEGIN CatFeeder =================+
# LOGO:
# ..............(..../\\
# ...............)..(.')
# ..............(../..)
# ...............\\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: sql_constants.py
# CREATION DATE: 11-10-2025
# LAST Modified: 14:52:9 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of storing information that is required for the sql library, but is constant.
# // AR
# +==== END CatFeeder =================+

"""

from typing import List, Dict

# Constants for supported database targets.
TARGET: Dict[str, bool] = {
    "mysql": True,
    "mariadb": True,
    "sqlite": False,
    "postgresql": False,
    "sqlexpress": False,
    "microsoft sql server": False
}

# Arguments to remove if empty or None.
UNWANTED_ARGUMENTS = [
    "option_files"
]

# Keywords considered risky for SQL sanitization.
RISKY_KEYWORDS: List[str] = [
    'add', 'all', 'alter', 'analyze', 'as', 'asc', 'asensitive', 'before',
    'bigint', 'binary', 'blob', 'by', 'call', 'cascade', 'case', 'change', 'char',
    'character', 'check', 'collate', 'column', 'condition', 'constraint', 'continue',
    'convert', 'create', 'cross', 'cursor', 'database', 'databases', 'day_hour',
    'day_microsecond', 'day_minute', 'day_second', 'dec', 'decimal', 'declare', 'default',
    'delayed', 'delete', 'desc', 'describe', 'deterministic', 'distinctrow', 'div', 'double', 'drop',
    'dual', 'each', 'else', 'elseif', 'exit', 'explain',
    'fetch', 'float', 'for', 'foreign', 'from', 'fulltext', 'general',
    'grant', 'group', 'high_priority', 'hour_microsecond', 'hour_minute',
    'hour_second', 'if', 'ignore', 'index', 'infile', 'inner', 'inout',
    'insensitive', 'insert', 'int', 'integer', 'interval', 'into', 'iterate',
    'key', 'keys', 'kill', 'leave', 'left', 'linear', 'lines',
    'load', 'localtime', 'localtimestamp', 'lock', 'long', 'longblob', 'longtext', 'loop',
    'low_priority', 'master_ssl_verify_server_cert', 'match', 'maxvalue', 'mediumblob',
    'mediumint', 'mediumtext', 'middleint', 'minute_microsecond', 'minute_second',
    'modifies', 'natural', 'no_write_to_binlog', 'numeric', 'on', 'optimize',
    'option', 'optionally', 'order', 'out', 'outer', 'outfile', 'precision', 'primary',
    'procedure', 'purge', 'range', 'read', 'reads', 'read_write', 'real', 'references',
    'release', 'rename', 'repeat', 'replace', 'require', 'resignal', 'restrict',
    'return', 'revoke', 'right', 'schema', 'schemas', 'second_microsecond',
    'select', 'sensitive', 'separator', 'set', 'show', 'signal', 'smallint', 'spatial',
    'specific', 'sql', 'sqlexception', 'sqlstate', 'sqlwarning', 'sql_big_result',
    'sql_calc_found_rows', 'sql_small_result', 'ssl', 'straight_join',
    'table', 'then', 'tinyblob', 'tinyint', 'tinytext', 'to',
    'trigger', 'undo', 'unique', 'unlock', 'update', 'usage',
    'use', 'using', 'values', 'varbinary', 'varchar', 'varcharacter',
    'when', 'where', 'while', 'with', 'write', 'year_month'
]

# Logical gates used in SQL queries.
KEYWORD_LOGIC_GATES: List[str] = [
    'and', 'or', 'not', 'xor', 'between', 'in', 'is', 'like', 'regexp', 'rlike',
    # 'null',
    'true', 'false', 'exists',
    'distinct', 'limit', 'having', 'join', 'union', 'current_date', 'current_time', 'current_timestamp', 'utc_date',
    'utc_time', 'utc_timestamp', 'mod', 'if'
]

# Date format constants.
DATE_ONLY: str = '%Y-%m-%d'
DATE_AND_TIME: str = '%Y-%m-%d %H:%M:%S'

# Error messages for database operations.
CONNECTION_FAILED: str = "Connection to the database is non-existent, aborting command."
CURSOR_FAILED: str = "Cursor to the database is non-existent, aborting command."

# Specific error codes.
GET_TABLE_SIZE_ERROR: int = -1

# Risky SQL DDL trigger keywords.
SQL_RISKY_DDL_TRIGGER_KEYWORDS: List[str] = [
    "drop ", "alter ", "truncate ", "create database",
    "use ", "grant ", "revoke ", "load data", "outfile", "infile"
]
