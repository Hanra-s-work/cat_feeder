<!-- 
-- +==== BEGIN CatFeeder =================+
-- LOGO: 
-- ..........####...####..........
-- ......###.....#.#########......
-- ....##........#.###########....
-- ...#..........#.############...
-- ...#..........#.#####.######...
-- ..#.....##....#.###..#...####..
-- .#.....#.##...#.##..##########.
-- #.....##########....##...######
-- #.....#...##..#.##..####.######
-- .#...##....##.#.##..###..#####.
-- ..#.##......#.#.####...######..
-- ..#...........#.#############..
-- ..#...........#.#############..
-- ...##.........#.############...
-- ......#.......#.#########......
-- .......#......#.########.......
-- .........#####...#####.........
-- /STOP
-- PROJECT: CatFeeder
-- FILE: oauth.md
-- CREATION DATE: 04-12-2025
-- LAST Modified: 10:41:33 04-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The file explaining how the OAuth class works.
-- // AR
-- +==== END CatFeeder =================+
-->
# OAuth Authentication

This document describes the `OAuthAuthentication` helper used by the backend to manage OAuth provider configuration, authorization flows and token exchange.

Location

- Source implementation: `backend/src/libs/utils/oauth_authentication.py`

Overview

- The `OAuthAuthentication` class centralises OAuth provider lifecycle: adding providers, generating authorization URLs, exchanging authorization codes for tokens, fetching user information and registering active OAuth connections for users.

- It relies on database tables defined by constants (e.g. `TAB_USER_OAUTH_CONNECTION`, `TAB_VERIFICATION`, `TAB_ACTIVE_OAUTHS`, `TAB_ACCOUNTS`) to persist provider configuration and active connections.

Key responsibilities

- Generate provider-specific authorization URLs (with state and expiration tracking).

- Exchange authorization codes for access tokens and refresh tokens.

- Retrieve user information from provider `user_info` endpoints.

- Create or link users in the local accounts table and record active OAuth connections.

- Add, update, patch and delete OAuth provider configuration (admin actions).

Important configuration

- Redirect URI: `CONST.REDIRECT_URI` (used when generating authorization URLs and exchanging codes).

- Providers are stored in the `TAB_USER_OAUTH_CONNECTION` database table. Provider rows are expected to include fields such as `client_id`, `client_secret`, `authorisation_base_url`, `token_grabber_base_url`, and `user_info_base_url`.

Class: OAuthAuthentication

Constructor

- __init__(success: int = 0, error: int = 84, debug: bool = False)
  - Initializes helper dependencies via `RuntimeManager` (database, boilerplates, headers).

Primary public endpoints / methods

- `async oauth_login(request: Request) -> Response`
  - Expects a JSON body containing `provider`.
  - Returns a JSON response with `authorization_url` on success.

- `async oauth_callback(request: Request) -> Response`
  - Endpoint to receive the OAuth provider callback (expects query params `code` and `state`).
  - Validates the state token saved during authorization URL generation and exchanges the `code` for tokens.
  - On success, logs/creates the user and returns authentication token via existing login flow.

- `async add_oauth_provider(request: Request, provider: str)`
  - Admin-only endpoint to add a provider row to `TAB_USER_OAUTH_CONNECTION`.
  - Required fields in request body: `client_id`, `client_secret`, `provider_scope`, `authorisation_base_url`, `token_grabber_base_url`, `user_info_base_url`.

- `async update_oauth_provider_data(request: Request, provider: str)`
  - Admin-only: replace all provider fields.

- `async patch_oauth_provider_data(request: Request, provider: str)`
  - Admin-only: patch selected provider fields.

- `async delete_oauth_provider(request: Request, provider: str)`
  - Admin-only: remove provider configuration and active connections.

- `refresh_token(provider_name: str, refresh_link: str) -> Union[str, None]`
  - Refresh access token for certain providers (google, discord, spotify).

Internal helpers (high-level)

- `_generate_oauth_authorization_url(provider: str) -> Union[int,str]`
  - Builds the authorization URL including a generated `state` token and stores verification entry in `TAB_VERIFICATION` with an expiration.

- `_exchange_code_for_token(provider: str, code: str)`
  - Posts to provider `token_grabber_base_url` to exchange `code` for tokens. Returns parsed token response or an error response.

- `_get_user_info(provider: str, access_token: str)`
  - Calls provider `user_info_base_url` with `Authorization: Bearer <token>` to retrieve user profile/email.

- `_oauth_user_logger(user_info: Dict, provider: str, connection_data: list) -> Response`
  - Creates or links a local user account, stores active oauth connection in `TAB_ACTIVE_OAUTHS`, and issues an application token via `BoilerplateIncoming.log_user_in()`.

- `_handle_token_response(token_response: Dict, provider: str) -> Response`
  - Processes token response returned by `_exchange_code_for_token`, extracts expiry/refresh token and delegates to `_oauth_user_logger`.

Expected database interactions (high level)

- `TAB_USER_OAUTH_CONNECTION` stores provider configuration.
- `TAB_VERIFICATION` stores temporary `state` values used to protect callback flows.
- `TAB_ACCOUNTS` stores user accounts; `TAB_ACTIVE_OAUTHS` stores active oauth connections linking `service_id` and `user_id`.

Example endpoints (registered by EndpointManager/PathManager)

- `POST /api/v1/oauth/login`  — body {"provider": "google"} — returns an `authorization_url` for the client to follow.
- `GET /api/v1/oauth/callback` — provider callback (query: `code`, `state`).
- `POST /api/v1/oauth/{provider}` — add oauth provider (admin).

Security and notes

- Admin-only methods are protected via token checks performed through shared boilerplate utilities.
- The implementation expects valid provider configuration in the DB; adding or updating providers must be done via authorized admin endpoints.

References

- Source: `backend/src/libs/utils/oauth_authentication.py`
- See also: `manual_documentation/endpoint_manager/endpoint_manager.md` for how OAuth endpoints are registered.

TODO

- Add provider examples for Google/GitHub with example `CLIENT_ID`/`CLIENT_SECRET` environment guidance (do not commit secrets).

Overview

- The `OAuthAuthentication` class centralises OAuth provider lifecycle: adding providers, generating authorization URLs, exchanging authorization codes for tokens, fetching user information and registering active OAuth connections for users.

- It relies on database tables defined by constants (e.g. `TAB_USER_OAUTH_CONNECTION`, `TAB_VERIFICATION`, `TAB_ACTIVE_OAUTHS`, `TAB_ACCOUNTS`) to persist provider configuration and active connections.

Key responsibilities

- Generate provider-specific authorization URLs (with state and expiration tracking).

- Exchange authorization codes for access tokens and refresh tokens.

- Retrieve user information from provider `user_info` endpoints.

- Create or link users in the local accounts table and record active OAuth connections.

- Add, update, patch and delete OAuth provider configuration (admin actions).

Important configuration

- Redirect URI: `CONST.REDIRECT_URI` (used when generating authorization URLs and exchanging codes).

- Providers are stored in the `TAB_USER_OAUTH_CONNECTION` database table. Provider rows are expected to include fields such as `client_id`, `client_secret`, `authorisation_base_url`, `token_grabber_base_url`, and `user_info_base_url`.

Class: OAuthAuthentication

Constructor

- __init__(success: int = 0, error: int = 84, debug: bool = False)
  - Initializes helper dependencies via `RuntimeManager` (database, boilerplates, headers).

Primary public endpoints / methods

- `async oauth_login(request: Request) -> Response`
  - Expects a JSON body containing `provider`.
  - Returns a JSON response with `authorization_url` on success.

- `async oauth_callback(request: Request) -> Response`
  - Endpoint to receive the OAuth provider callback (expects query params `code` and `state`).
  - Validates the state token saved during authorization URL generation and exchanges the `code` for tokens.
  - On success, logs/creates the user and returns authentication token via existing login flow.

- `async add_oauth_provider(request: Request, provider: str)`
  - Admin-only endpoint to add a provider row to `TAB_USER_OAUTH_CONNECTION`.
  - Required fields in request body: `client_id`, `client_secret`, `provider_scope`, `authorisation_base_url`, `token_grabber_base_url`, `user_info_base_url`.

- `async update_oauth_provider_data(request: Request, provider: str)`
  - Admin-only: replace all provider fields.

- `async patch_oauth_provider_data(request: Request, provider: str)`
  - Admin-only: patch selected provider fields.

- `async delete_oauth_provider(request: Request, provider: str)`
  - Admin-only: remove provider configuration and active connections.

- `refresh_token(provider_name: str, refresh_link: str) -> Union[str, None]`
  - Refresh access token for certain providers (google, discord, spotify).

Internal helpers (high-level)

- `_generate_oauth_authorization_url(provider: str) -> Union[int,str]`
  - Builds the authorization URL including a generated `state` token and stores verification entry in `TAB_VERIFICATION` with an expiration.

- `_exchange_code_for_token(provider: str, code: str)`
  - Posts to provider `token_grabber_base_url` to exchange `code` for tokens. Returns parsed token response or an error response.

- `_get_user_info(provider: str, access_token: str)`
  - Calls provider `user_info_base_url` with `Authorization: Bearer <token>` to retrieve user profile/email.

- `_oauth_user_logger(user_info: Dict, provider: str, connection_data: list) -> Response`
  - Creates or links a local user account, stores active oauth connection in `TAB_ACTIVE_OAUTHS`, and issues an application token via `BoilerplateIncoming.log_user_in()`.

- `_handle_token_response(token_response: Dict, provider: str) -> Response`
  - Processes token response returned by `_exchange_code_for_token`, extracts expiry/refresh token and delegates to `_oauth_user_logger`.

Expected database interactions (high level)

- `TAB_USER_OAUTH_CONNECTION` stores provider configuration.
- `TAB_VERIFICATION` stores temporary `state` values used to protect callback flows.
- `TAB_ACCOUNTS` stores user accounts; `TAB_ACTIVE_OAUTHS` stores active oauth connections linking `service_id` and `user_id`.

Example endpoints (registered by EndpointManager/PathManager)

- `POST /api/v1/oauth/login`  — body {"provider": "google"} — returns an `authorization_url` for the client to follow.
- `GET /api/v1/oauth/callback` — provider callback (query: `code`, `state`).
- `POST /api/v1/oauth/{provider}` — add oauth provider (admin).

Security and notes

- Admin-only methods are protected via token checks performed through shared boilerplate utilities.
- The implementation expects valid provider configuration in the DB; adding or updating providers must be done via authorized admin endpoints.

References

- Source: `backend/src/libs/utils/oauth_authentication.py`
- See also: `manual_documentation/endpoint_manager/endpoint_manager.md` for how OAuth endpoints are registered.

TODO

- Add provider examples for Google/GitHub with example `CLIENT_ID`/`CLIENT_SECRET` environment guidance (do not commit secrets).
