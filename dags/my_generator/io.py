import pathlib
import yaml

DIR = pathlib.Path(__file__).parent.absolute()
PIPELINE_CONFIGS_DIR = DIR / "pipeline_configs"


def _all_pipeline_configs_files():
    return [
        config for config in PIPELINE_CONFIGS_DIR.glob("**/*.yaml") if config.is_file()
    ]


def all_pipeline_configs():
    for config in _all_pipeline_configs_files():
        with config.open() as f:
            yield yaml.safe_load(f)


if __name__ == "__main__":
    for config in all_pipeline_configs():
        print(config)
