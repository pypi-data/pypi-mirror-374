from nlbone.adapters.http_clients.uploadchi import UploadchiClient
from nlbone.adapters.http_clients.uploadchi_async import UploadchiAsyncClient
from nlbone.config.settings import Settings
from nlbone.adapters.auth.keycloak import KeycloakAuthService
from nlbone.core.ports.files import FileServicePort, AsyncFileServicePort


class Container:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.auth: KeycloakAuthService = KeycloakAuthService(self.settings)
        self.file_service: FileServicePort = UploadchiClient()
        self.afiles_service: AsyncFileServicePort = UploadchiAsyncClient()
