import os
import subprocess
from pprint import pprint

import typer
from atptools import DictDefault
from pydantic import BaseModel

default_config_path: str = "./atprun.yml"


class AtpRunScript(BaseModel):
    run: str
    name: str | None = None
    # description: str | None = None
    # env_var:
    # env_files: list[str] | None = None
    # dot_env_group: str | None = None
    # uv_group


class AtpRunConfig(BaseModel):
    scripts: dict[str, AtpRunScript]
    # pipelines: dict[str, list[str]] = {}


class AtpRunScriptRun:
    def __init__(self, name: str, script: AtpRunScript) -> None:
        self.name: str = name
        self.script: AtpRunScript = script
        return None

    def run(self) -> None:
        command: str = self.script.run
        if len(command) <= 0:
            raise ValueError("No 'run' is empty")
        subprocess.run(
            args=command,
            shell=True,
        )
        return None


class AtpRunMain:
    def __init__(self) -> None:
        self.config_path: str = ""
        self.config_in: DictDefault = DictDefault()
        self.config: AtpRunConfig | None = None
        self.scripts_run: dict[str, AtpRunScriptRun] = {}
        return None

    def _get_configuration_file_path(self, path: str | None) -> str:
        # Load default value
        self.config_path = default_config_path
        # Load environment variable
        if "ATPRUN_CONFIG_PATH" in os.environ:
            self.config_path = os.environ["ATPRUN_CONFIG_PATH"]
        # Load command line argument
        if path is not None and len(path) > 0:
            self.config_path = path

        return self.config_path

    def load_configuration(self, path: str | None) -> None:
        self._get_configuration_file_path(path=path)

        self.config_in.from_file(path=self.config_path)

        self.config = AtpRunConfig.model_validate(
            obj=self.config_in.to_dict(),
            strict=True,
        )

        # prepare scripts run
        if self.config.scripts is not None:
            for name, script in self.config.scripts.items():
                self.scripts_run[name] = AtpRunScriptRun(
                    name=name,
                    script=script,
                )
        return None

    def script_get(self, name) -> AtpRunScriptRun:
        try:
            return self.scripts_run[name]
        except KeyError as err:
            raise ValueError(f"Script '{name}' not found") from err

    def script_run(self, name: str) -> None:
        script: AtpRunScriptRun = self.script_get(name=name)
        script.run()
        return None
