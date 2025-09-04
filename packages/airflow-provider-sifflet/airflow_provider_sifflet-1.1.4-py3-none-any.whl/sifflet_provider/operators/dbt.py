from typing import Sequence

from airflow.models.baseoperator import BaseOperator
from airflow.utils.trigger_rule import TriggerRule
from sifflet_provider.hooks.sifflet_hook import SiffletHook
from sifflet_sdk.ingest.service import IngestionService


class SiffletDbtIngestOperator(BaseOperator):
    ui_color = "#fff"
    ui_fgcolor = "#113e60"

    template_fields: Sequence[str] = (
        "project_name",
        "target",
        "input_folder",
    )

    def __init__(  # pylint: disable=R0913
        self,
        project_name: str,
        target: str,
        input_folder: str,
        sifflet_conn_id: str = "sifflet_default",
        trigger_rule: TriggerRule = TriggerRule.ALL_DONE,
        **kwargs,
    ) -> None:
        """
        Operator to ingest dbt metadata files into Sifflet

        Args:
            project_name (str): The name of your dbt project (in your dbt_project.yml file)
            target (str): The target value of the profile (in your dbt_project.yml file)
            input_folder (str): The dbt execution folder
            sifflet_conn_id (str): Airflow Sifflet connection ID
            trigger_rule (TriggerRule): defines the rule by which dependencies are applied for the task to get triggered. Default = "all_done"
        """
        super().__init__(trigger_rule=trigger_rule, **kwargs)
        self.project_name = project_name
        self.target = target
        self.input_folder = input_folder
        self.sifflet_conn_id = sifflet_conn_id

    def execute(self, context):
        hook = SiffletHook(sifflet_conn_id=self.sifflet_conn_id)
        service = IngestionService(sifflet_config=hook.get_conn())
        return service.ingest_dbt(
            project_name=self.project_name,
            target=self.target,
            input_folder=self.input_folder,
        )
