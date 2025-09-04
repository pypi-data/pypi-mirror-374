import sifflet_provider


def get_provider_info():
    return {
        "package-name": "airflow-provider-sifflet",
        "name": "Sifflet",
        "description": "`Sifflet <https://www.siffletdata.com/>`__",
        "versions": [
            sifflet_provider.__version__,
        ],
        "additional-dependencies": ["apache-airflow>=2.0.0"],
        "operators": [
            {
                "integration-name": "Sifflet Run Rule",
                "python-modules": ["sifflet_provider.operators.rule"],
            },
            {
                "integration-name": "Sifflet Ingest dbt",
                "python-modules": ["sifflet_provider.operators.dbt"],
            },
        ],
        "connection-types": [
            {
                "hook-class-name": "sifflet_provider.hooks.sifflet_hook.SiffletHook",
                "connection-type": "sifflet",
            },
        ],
    }
