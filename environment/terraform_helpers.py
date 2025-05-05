import subprocess
from typing import Optional
import os

from config.Config import LLMAPIKeys


def deploy_network(
    name, use_credentials=True, llm_api_keys: Optional[LLMAPIKeys] = None
):
    deployment_dir = os.path.join("environment/topologies", name)
    subprocess.run(
        ["terraform", "init"], cwd=deployment_dir, capture_output=True, text=True
    )

    env_vars = os.environ.copy()

    if llm_api_keys is not None:
        env_vars["TF_VAR_openai_api_key"] = llm_api_keys.open_ai
        env_vars["TF_VAR_anthropic_api_key"] = llm_api_keys.anthropic
        env_vars["TF_VAR_google_api_key"] = llm_api_keys.google

    if use_credentials:
        process = subprocess.Popen(
            [
                "terraform",
                "apply",
                "-var-file=../../credentials.tfvars",
                "-auto-approve",
            ],
            cwd=deployment_dir,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            # env=env_vars,
        )
    else:
        process = subprocess.Popen(
            ["terraform", "apply", "-auto-approve"],
            cwd=deployment_dir,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            env=env_vars,
        )

    stdout, stderr = process.communicate()


def destroy_network(name, use_credentials=True):
    deployment_dir = os.path.join("environment/topologies", name)
    subprocess.run(
        ["terraform", "init"], cwd=deployment_dir, capture_output=True, text=True
    )

    if use_credentials:
        process = subprocess.Popen(
            [
                "terraform",
                "destroy",
                "-var-file=../../credentials.tfvars",
                "-auto-approve",
            ],
            cwd=deployment_dir,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
    else:
        process = subprocess.Popen(
            ["terraform", "destroy", "-auto-approve"],
            cwd=deployment_dir,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

    stdout, stderr = process.communicate()
