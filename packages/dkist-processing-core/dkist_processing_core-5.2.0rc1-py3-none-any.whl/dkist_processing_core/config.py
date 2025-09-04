"""Environment controlled configurations for dkist_processing_core."""

from dkist_service_configuration import MeshServiceConfigurationBase
from dkist_service_configuration.settings import MeshService
from pydantic import Field
from talus import ConnectionRetryerFactory
from talus import Exchange
from talus.models.connection_parameters import ConnectionParameterFactory


class DKISTProcessingCoreConfiguration(MeshServiceConfigurationBase):
    """Environment configurations for dkist_processing_core."""

    isb_username: str = Field(default="guest")
    isb_password: str = Field(default="guest")
    isb_exchange: str = Field(default="master.direct.x")
    isb_queue_type: str = Field(default="classic")
    elastic_apm_service_name: str = Field(default="dkist-processing-core")
    elastic_apm_other_options: dict = Field(default_factory=dict)
    elastic_apm_enabled: bool = False
    build_version: str = Field(default="dev")

    @property
    def isb_mesh_service(self) -> MeshService:
        """Return the mesh service details for the interservice-bus."""
        return self.service_mesh_detail(
            service_name="interservice-bus",
            default_mesh_service=MeshService(mesh_address="localhost", mesh_port=5672),
        )

    @property
    def isb_producer_connection_parameters(self) -> ConnectionParameterFactory:
        """Return the connection parameters for the ISB producer."""
        return ConnectionParameterFactory(
            rabbitmq_host=self.isb_mesh_service.host,
            rabbitmq_port=self.isb_mesh_service.port,
            rabbitmq_user=self.isb_username,
            rabbitmq_pass=self.isb_password,
            connection_name="dkist-processing-core-producer",
        )

    @property
    def isb_connection_retryer(self) -> ConnectionRetryerFactory:
        """Return the connection retryer for the ISB connection."""
        return ConnectionRetryerFactory(
            delay_min=1,
            delay_max=5,
            backoff=1,
            jitter_min=1,
            jitter_max=3,
            attempts=3,
        )

    @property
    def isb_queue_arguments(self) -> dict:
        """Return the queue arguments for the ISB."""
        return {
            "x-queue-type": self.isb_queue_type,
        }

    @property
    def isb_publish_exchange(self) -> Exchange:
        """Return the exchange for the ISB."""
        return Exchange(name=self.isb_exchange)

    @property
    def elastic_apm_server_url(self) -> str:
        """Return the URL for the Elastic APM server."""
        apm_server = self.service_mesh_detail(service_name="system-monitoring-log-apm")
        return f"http://{apm_server.host}:{apm_server.port}/"

    @property
    def apm_config(self) -> dict:
        """Return the configuration for the Elastic APM."""
        return {
            "SERVICE_NAME": self.elastic_apm_service_name,
            "SERVER_URL": self.elastic_apm_server_url,
            "ENVIRONMENT": "Workflows",
            **self.elastic_apm_other_options,
        }


core_configurations = DKISTProcessingCoreConfiguration()
