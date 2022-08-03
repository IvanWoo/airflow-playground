from schema import Schema, And, Or, Use
from croniter import croniter

METADATA_SCHEMA = Schema(
    {
        "dag_id": And(str, len),
        "owner": And(str, len),
        "retries": And(Use(int), lambda x: 0 <= x <= 3),
        "cron": And(
            Or(str, None), lambda x: croniter.is_valid(x) if x is not None else True
        ),
    }
)

PIPELINE_CONFIG_SCHEMA = Schema({"api_version": "1.0", "metadata": METADATA_SCHEMA})
