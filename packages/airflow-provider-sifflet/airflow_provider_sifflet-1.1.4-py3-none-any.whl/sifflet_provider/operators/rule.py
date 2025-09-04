from typing import List, Sequence

from airflow.models.baseoperator import BaseOperator
from sifflet_provider.hooks.sifflet_hook import SiffletHook
from sifflet_sdk.rules.service import RulesService


class SiffletRunRuleOperator(BaseOperator):
    ui_color = "#fff"
    ui_fgcolor = "#113e60"

    template_fields: Sequence[str] = ("rule_ids",)

    def __init__(
        self, rule_ids: List[str], error_on_rule_fail: bool = True, sifflet_conn_id: str = "sifflet_default", **kwargs
    ) -> None:
        """
        Run one or several Sifflet rules and wait for their result.

        Args:
            rule_ids (List[str]): The list of rule ids to trigger
            error_on_rule_fail (bool): Mark the Airflow task as Fail or Success if the Sifflet rule Fail
            sifflet_conn_id (str): Airflow Sifflet connection ID
        """
        super().__init__(**kwargs)
        self.rule_ids = rule_ids
        self.error_on_rule_fail = error_on_rule_fail
        self.sifflet_conn_id = sifflet_conn_id

    def execute(self, context):
        hook = SiffletHook(sifflet_conn_id=self.sifflet_conn_id)

        service = RulesService(sifflet_config=hook.get_conn())
        rule_runs = service.run_rules(rule_ids=self.rule_ids)
        service.wait_rule_runs(rule_runs=rule_runs, error_on_rule_fail=self.error_on_rule_fail)
