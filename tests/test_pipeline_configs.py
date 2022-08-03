from dags.my_generator.io import get_all_pipeline_configs
from dags.my_generator.pipeline_config_schema import PIPELINE_CONFIG_SCHEMA


def test_pipeline_configs():
    for config in get_all_pipeline_configs():
        validated_config = PIPELINE_CONFIG_SCHEMA.validate(config)
        assert validated_config is not None
