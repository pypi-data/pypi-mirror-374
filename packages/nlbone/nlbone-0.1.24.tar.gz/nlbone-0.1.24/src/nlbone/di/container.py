from nlbone.config.settings import Settings
from nlbone.adapters.auth.keycloak import KeycloakAuthService

class Container:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.auth: KeycloakAuthService = KeycloakAuthService(self.settings)