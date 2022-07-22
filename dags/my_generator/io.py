import pathlib
import yaml

DIR = pathlib.Path(__file__).parent.absolute()
PIPELINE_CONFIGS_DIR = DIR / "pipeline_configs"


def _get_all_pipeline_configs_files():
    return [
        config for config in PIPELINE_CONFIGS_DIR.glob("**/*.yaml") if config.is_file()
    ]


def get_all_pipeline_configs():
    for config in _get_all_pipeline_configs_files():
        with config.open() as f:
            yield yaml.safe_load(f)


def get_all_dag_ids():
    return [
        config["metadata"]["dag_id"].strip() for config in get_all_pipeline_configs()
    ]


if __name__ == "__main__":
    for config in get_all_pipeline_configs():
        print(config)
