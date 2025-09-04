Sifflet Provider for Apache Airflow
=================================

This package provides operators and hook that integrate [Sifflet](https://www.siffletdata.com/) into Apache Airflow.
All classes for this provider package are in the `sifflet_provider` Python package.

## Installation

You can install this package on top of an existing Airflow 2.1+ installation

```shell
pip install airflow-provider-sifflet
```

The package supports the following python versions: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12

## Configuration

In the Airflow user interface, you can configure a Connection for Sifflet in
`Admin` -> `Connections` -> `Add a new record`.

You will need to fill out the following:

    Connection Id: sifflet_default
    Connection Type: Sifflet
    Sifflet Tenant: <your_tenant_name> (for SaaS deployment)
    Sifflet Backend URL: <your_backend_url> (for Self-hosted deployment)
    Sifflet Token: <your_sifflet_access_token>

`<your_sifflet_access_token>`: you can find more information on how to generate it [here](https://docs.siffletdata.com/docs/generate-an-api-token)

One of these two parameters is required, depending on your type of Sifflet deployment:
- **SaaS deployments**: `Sifflet Tenant`, if you access Sifflet with `https://abcdef.siffletdata.com`, then your tenant would be `abcdef`
- **Self-hosted deployments**: `Sifflet Backend URL`, full URL to the Sifflet backend on your deployment, for instance: `https://sifflet-backend.mycompany.com`

## Modules

### Operators

#### _SiffletDbtIngestOperator_

`SiffletDbtIngestOperator` sends your DBT artifacts to the Sifflet application.

Example usage:

```python
from sifflet_provider.operators.dbt import SiffletDbtIngestOperator

sifflet_dbt_ingest = SiffletDbtIngestOperator(
    task_id="sifflet_dbt_ingest",
    input_folder="<path to dbt project folder>",
    target="prod",
    project_name="<dbt project name>",
)
```

#### _SiffletRunRuleOperator_

`SiffletRunRuleOperator` Run one or several Sifflet rules - requires rule id(s).

Example usage:

```python
from sifflet_provider.operators.rule import SiffletRunRuleOperator

sifflet_run_rule = SiffletRunRuleOperator(
    task_id="sifflet_run_rule",
    rule_ids=[
        "3e2e2687-cd20-11ec-b38b-06bb20181849",
        "3e19eb3e-cd20-11ec-b38b-06bb20181849",
        "3e1a86f1-cd20-11ec-b38b-06bb20181849",
        "3e2e1fc3-cd20-11ec-b38b-06bb20181849",
    ],
    error_on_rule_fail=True
)
```
