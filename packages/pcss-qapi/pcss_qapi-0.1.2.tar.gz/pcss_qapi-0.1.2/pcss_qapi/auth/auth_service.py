"""Authorization service for pcss_qapi"""
import json
import os

import hashlib

from pcss_qapi.auth.oauth_flow import OAuthManager
from pcss_qapi.utils.fs_manager import FSManager, API_KEY_FILE_NAME

from pcss_qapi.base.connection_base import ApiConnection
from pcss_qapi.auth.connections import PcssQapiConnection

OAUTH_MANAGERS: dict[str, OAuthManager] = {}


def get_manager_for_connection(connection: ApiConnection) -> OAuthManager:
    """Get oauth manager for given connection type, create new if not existing"""
    connection_manager = OAUTH_MANAGERS.get(str(hash(connection)), None)
    if connection_manager is None:
        connection_manager = OAuthManager(
            connection.oauth_client_id,
            connection.oauth_issuer,
            connection.oauth_min_ttl_seconds
        )
        OAUTH_MANAGERS[str(hash(connection))] = connection_manager
    return connection_manager


def get_hash(issuer: str, client_id: str) -> str:
    """get hash for connection"""
    return hashlib.sha256(f'{issuer}{client_id}'.encode('utf-8')).hexdigest()


class AuthorizationService:
    """
    Authentication and login handler for pcss_qapi service
    """

    @staticmethod
    def _get_functional_tokens(oauth_manager: OAuthManager) -> tuple[str | None, str | None]:
        """Get access and refresh tokens, refresh if necessary."""
        storage_path = FSManager.get_storage_path()
        filepath = os.path.join(storage_path, API_KEY_FILE_NAME)

        if not os.path.exists(filepath):
            return None, None

        key_hash = get_hash(oauth_manager.issuer, oauth_manager.client_id)

        access_token, refresh_token = None, None
        with open(filepath, 'r', encoding='UTF-8') as f:
            key_infos = json.loads(f.read())
            key_info = key_infos.get(key_hash, None)
            if key_info is None:
                return None, None

            access_token, refresh_token = key_info.get('access_token', None), key_info.get('refresh_token', None)
            if access_token is None or refresh_token is None:
                return None, None

            if not oauth_manager.is_token_valid(access_token):
                access_token, refresh_token = oauth_manager.get_refreshed_tokens(refresh_token)

        if access_token is not None and refresh_token is not None:
            FSManager.update_credentials(
                key_hash,
                {
                    'refresh_token': refresh_token,
                    'access_token': access_token
                })  # Save refreshed tokens

        return access_token, refresh_token

    @staticmethod
    def login(
        connection: ApiConnection = PcssQapiConnection,
    ):
        """
        Cache api key string for later use.

        Args:
        """
        storage_location = FSManager.get_storage_path()

        storage_path = FSManager.get_fixed_path(storage_location)
        os.makedirs(storage_path, exist_ok=True)

        connection_manager = get_manager_for_connection(connection)
        key_hash = get_hash(connection_manager.issuer, connection_manager.client_id)

        access_token, refresh_token = AuthorizationService._get_functional_tokens(connection_manager)
        if access_token is not None and refresh_token is not None:
            print("ℹ️ Using cached tokens. If you want to change the account use AuthorizationService.logout() first.")
            return

        access_token, refresh_token = connection_manager.get_device_flow_tokens()
        if access_token is None or refresh_token is None:
            raise ValueError("Authorization error, did not receive tokens.")

        FSManager.update_credentials(
            key_hash,
            {
                'refresh_token': refresh_token,
                'access_token': access_token
            })

    @staticmethod
    def logout(
        connection: ApiConnection | None = None
    ):
        """Remove credentials for active account"""

        filepath = os.path.join(FSManager.get_storage_path(), API_KEY_FILE_NAME)
        if connection is None:
            if os.path.exists(filepath):
                os.remove(filepath)
            return

        FSManager.remove_credentials(
            get_hash(connection.oauth_issuer, connection.oauth_client_id)
        )

    @staticmethod
    def get_api_key(connection: ApiConnection) -> str:
        """Get api key string if available. Automatically logs out if unable to refresh key."""

        connection_manager = get_manager_for_connection(connection)
        access_token, _ = AuthorizationService._get_functional_tokens(connection_manager)
        if access_token is None:
            AuthorizationService.logout()
            raise ValueError("Use AuthorizationService.login()")
        return access_token
