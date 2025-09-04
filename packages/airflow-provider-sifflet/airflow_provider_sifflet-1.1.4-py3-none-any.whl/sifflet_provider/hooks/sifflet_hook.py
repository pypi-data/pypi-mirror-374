from typing import Dict

from airflow.hooks.base import BaseHook
from sifflet_sdk.config import SiffletConfig
from sifflet_sdk.status.service import StatusService

APPLICATION_NAME_AIRFLOW_PROVIDER_SIFFLET = "airflow-provider-sifflet"


class SiffletHook(BaseHook):
    """
    Hook for Sifflet interaction.

    This hook requires authentication details:
      - Sifflet tenant - For Sifflet SaaS version, the tenant matches the prefix of your Sifflet URL.
      - Sifflet URL - For self-hosted deployment, full URL to the Sifflet backend.
      - Sifflet Access Token - The access token must be generated in the Web UI of Sifflet.

    Args:
        sifflet_conn_id (str): The connection ID to use when fetching connection info.
    """

    conn_name_attr = "sifflet_conn_id"
    default_conn_name = "sifflet_default"
    conn_type = "sifflet"
    hook_name = "Sifflet"

    def __init__(self, sifflet_conn_id: str = "sifflet_default") -> None:
        super().__init__()
        self.sifflet_conn_id = sifflet_conn_id

    @staticmethod
    def get_ui_field_behaviour() -> Dict:
        """Returns custom field behaviour"""
        return {
            "hidden_fields": ["login", "port"],
            "relabeling": {
                "password": "Sifflet Access Token",
                "host": "Sifflet Backend URL",
                "schema": "Sifflet Tenant",
            },
            "placeholders": {
                "schema": (
                    "For Sifflet SaaS deployment, name of your tenant. For instance, if you access to "
                    "Sifflet UI with https://mycompany.siffletdata.com, then your tenant would be mycompany"
                ),
                "host": (
                    "For self-hosted deployment, full URL to the Sifflet backend on your deployment, "
                    "for instance: https://sifflet-backend.mycompany.com"
                ),
                "password": "The access token must be generated in the Web UI of Sifflet Settings > Access-Tokens",
            },
        }

    def get_conn(self) -> SiffletConfig:
        """Returns the SiffletConfig for the current connection id."""
        conn = self.get_connection(self.sifflet_conn_id)
        conn_params = conn.extra_dejson

        tenant = conn.schema
        token = conn.password
        backend_url = conn.host
        debug = conn_params.get("debug", False)

        return SiffletConfig(
            tenant=tenant,
            backend_url=backend_url,
            token=token,
            debug=debug,
            application_name=APPLICATION_NAME_AIRFLOW_PROVIDER_SIFFLET,
        )

    def test_connection(self):
        """
        Test the Sifflet connection by calling check_status().
        Available since Airflow 2.2
        https://github.com/apache/airflow/blob/v2-2-stable/airflow/models/connection.py#L358
        https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#test-connection
        """
        try:
            config = self.get_conn()

            if not config.token:
                return False, "The Sifflet Access Token must be set."
            if not (config.tenant or config.backend_url):
                return False, "The Sifflet Tenant or Sifflet URL must be set."

            status_service = StatusService(config)
            result: bool = status_service.check_status()
            if result:
                return True, "Connection successfully tested"
            else:
                return False, "Connection error, check your parameters"
        except Exception:
            return False, "Connection error, check your parameters"
