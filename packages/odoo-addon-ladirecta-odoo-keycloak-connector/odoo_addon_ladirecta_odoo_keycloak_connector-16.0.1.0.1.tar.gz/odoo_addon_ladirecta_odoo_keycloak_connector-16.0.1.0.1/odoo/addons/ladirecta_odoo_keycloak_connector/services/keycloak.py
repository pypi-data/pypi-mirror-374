import logging

from keycloak import KeycloakAdmin, KeycloakOpenIDConnection

_logger = logging.getLogger(__name__)


class KeycloakService:
    def __init__(self, company):
        _logger.debug("Create Admin connection with Keycloak...")
        keycloak_connection = KeycloakOpenIDConnection(
            server_url=company.keycloak_url,
            username=company.keycloak_admin_user,
            password=company.keycloak_admin_password,
            user_realm_name=company.keycloak_user_realm_name,
            realm_name=company.keycloak_realm_name,
            client_id=company.keycloak_client_id,
            client_secret_key=company.keycloak_client_secret_master_realm,
            verify=True,
        )
        self.keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
        self.subs_keycloak_group_id = company.keycloak_subs_group_id
        _logger.debug("Admin connection created.")

    def create_keycloak_user(self, record):
        _logger.debug(f"Create the user for username {record.vat}")
        if not record.email:
            raise ValueError(
                "The partner used to create the user not has an email."
                "Please fill it to create the user."
            )
        try:
            user = self.keycloak_admin.create_user(
                {
                    "email": record.email,
                    "username": record.email,
                    "firstName": record.name,
                    "enabled": True,
                    "emailVerified": False,
                    "requiredActions": ["UPDATE_PASSWORD", "VERIFY_EMAIL"],
                    "attributes": {
                        "OdooID": record.id,
                    },
                },
                exist_ok=True,
            )
            record.keycloak_user_id = user
            self.keycloak_admin.group_user_add(
                user_id=user, group_id=self.subs_keycloak_group_id
            )
            # TODO: Discomment when the Keycloak initial migration ends
            # Update the password
            # self.keycloak_admin.send_update_account(
            #    user_id=user, payload=["UPDATE_PASSWORD"]
            # )
            _logger.debug(f"User created for partner ID {record.id}")
        except Exception as e:
            _logger.error(f"Error creating user for {record.id}: {e}")
