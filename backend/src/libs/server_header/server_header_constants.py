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
# FILE: server_header_constants.py
# CREATION DATE: 27-11-2025
# LAST Modified: 14:51:45 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The constants used in the Server Header class
# // AR
# +==== END CatFeeder =================+
"""

# Custom application headers
# Custom header to identify the application sending the response
HEADER_APP_NAME: str = "app_sender"

# Caching control headers
# Directives for caching mechanisms in browsers and proxies
CACHE_CONTROL: str = "Cache-Control"
# HTTP/1.0 backward-compatible cache control (deprecated but still used)
PRAGMA: str = "Pragma"
EXPIRES: str = "Expires"  # Date/time after which the response is considered stale

# Content delivery headers
# Indicates if content should be inline or attachment with filename
CONTENT_DISPOSITION: str = "Content-Disposition"

# Privacy and referrer headers
# Controls how much referrer information is sent with requests
REFERRER_POLICY: str = "Referrer-Policy"

# Range request headers
# Indicates server support for partial content requests (streaming/seeking)
ACCEPT_RANGES: str = "Accept-Ranges"

# Security headers
# Prevents XSS by controlling allowed content sources
CONTENT_SECURITY_POLICY: str = "Content-Security-Policy"
# Prevents MIME type sniffing attacks
CONTENT_TYPE: str = "X-Content-Type-Options"
# Prevents clickjacking by controlling iframe embedding
FRAME_OPTIONS: str = "X-Frame-Options"
# Enables browser's built-in XSS filter (legacy but still used)
XSS_PROTECTION: str = "X-XSS-Protection"
