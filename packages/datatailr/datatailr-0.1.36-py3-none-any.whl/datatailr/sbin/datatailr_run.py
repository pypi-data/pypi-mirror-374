#!/usr/bin/env python3

# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************


# The purpose of this script is to be the entrypoint for all jobs running on datatailr.
# The main functions of the script are:
#     1. Create a linux user and group for the job.
#     2. Set the environment variables for the job.
#     3. Run the job in a separate process, as the newly created user and pass all relevant environment variables.
# There are muliple environment variables which are required for the job to run.
# Some of them are necessary for the setup stage, which is executed directly in this script as the linux root user.
# Others are passed to the job script, which is executed in a separate process with only the users' privileges and not as a root user.
#
# Setup environment variables:
#     DATATAILR_USER - the user under which the job will run.
#     DATATAILR_GROUP - the group under which the job will run.
#     DATATAILR_UID - the user ID of the user as it is defined in the system.
#     DATATAILR_GID - the group ID of the group as it is defined in the system.
#     DATATAILR_JOB_TYPE - the type of job to run. (batch\service\app\excel\IDE)
# Job environment variables (not all are always relevant, depending on the job type):
#     DATATAILR_BATCH_RUN_ID - the unique identifier for the batch run.
#     DATATAILR_BATCH_ID - the unique identifier for the batch.
#     DATATAILR_JOB_ID - the unique identifier for the job.


import subprocess
import os
import sys
from typing import Tuple
from datatailr.logging import DatatailrLogger
from datatailr.utils import is_dt_installed

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()

if not is_dt_installed():
    logger.error("Datatailr is not installed.")
    # sys.exit(1) # TODO: Uncomment after testing


def get_env_var(name: str, default: str | None = None) -> str:
    """
    Get an environment variable.
    If the variable is not set, raise an error.
    """
    if name not in os.environ:
        if default is not None:
            return default
        logger.error(f"Environment variable '{name}' is not set.")
        raise ValueError(f"Environment variable '{name}' is not set.")
    return os.environ[name]


def create_user_and_group() -> Tuple[str, str]:
    """
    Create a user and group for the job.
    The user and group names are taken from the environment variables DATATAILR_USER and DATATAILR_GROUP.
    The group and user are created with the same uid and gid as passed in the environment variables DATATAILR_UID and DATATAILR_GID.
    If the user or group already exists, do nothing.
    """
    user = get_env_var("DATATAILR_USER")
    group = get_env_var("DATATAILR_GROUP")
    uid = get_env_var("DATATAILR_UID")
    gid = get_env_var("DATATAILR_GID")

    # Create group if it does not exist
    os.system(f"getent group {group} || groupadd {group} -g {gid} -o")

    # Create user if it does not exist
    os.system(
        f"getent passwd {user} || useradd -g {group} -s /bin/bash -m {user} -u {uid} -o"
    )
    return user, group


def run_command_as_user(command: str | list, user: str, env_vars: dict):
    """
    Run a command as a specific user with the given environment variables.
    """
    if isinstance(command, str):
        command = command.split(" ")
    env_vars = {
        "PATH": get_env_var("PATH", ""),
        "PYTHONPATH": get_env_var("PYTHONPATH", ""),
    } | env_vars

    env_kv = [f"{k}={v}" for k, v in env_vars.items()]
    argv = ["sudo", "-u", user, "env", *env_kv, "bash", "-lc", *command]

    try:
        result = subprocess.run(
            argv,
            check=True,  # raises if returncode != 0
            capture_output=True,
            text=True,
        )
        logger.info(f"stdout: {result.stdout}")
        logger.debug(f"stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"stderr: {e.stderr}")
        sys.exit(1)


def main():
    user, _ = create_user_and_group()
    job_type = get_env_var("DATATAILR_JOB_TYPE")

    env = {
        "DATATAILR_JOB_TYPE": job_type,
        "DATATAILR_JOB_NAME": get_env_var("DATATAILR_JOB_NAME"),
        "DATATAILR_JOB_ID": get_env_var("DATATAILR_JOB_ID"),
    }

    if job_type == "batch":
        run_id = get_env_var("DATATAILR_BATCH_RUN_ID")
        batch_id = get_env_var("DATATAILR_BATCH_ID")
        entrypoint = get_env_var("DATATAILR_BATCH_ENTRYPOINT")
        env = {
            "DATATAILR_BATCH_RUN_ID": run_id,
            "DATATAILR_BATCH_ID": batch_id,
            "DATATAILR_BATCH_ENTRYPOINT": entrypoint,
        } | env
        run_command_as_user("datatailr_run_batch", user, env)
    elif job_type == "service":
        port = get_env_var("DATATAILR_SERVICE_PORT")
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
            "DATATAILR_SERVICE_PORT": port,
        } | env
        run_command_as_user("datatailr_run_service", user, env)
    elif job_type == "app":
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
        } | env
        run_command_as_user("datatailr_run_app", user, env)
    elif job_type == "excel":
        host = get_env_var("DATATAILR_HOST", "")
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
            "DATATAILR_HOST": host,
        } | env
        run_command_as_user("datatailr_run_excel", user, env)
    elif job_type == "IDE":
        command = [
            "code-server",
            "--auth=none",
            "--bind-addr=0.0.0.0:8080",
            f'--app-name="Datatailr IDE {get_env_var("DATATAILR_USER")}"',
        ]
        run_command_as_user(command, user, env)
    elif job_type == "jupyter":
        command = [
            "jupyter-lab",
            "--ip='*'",
            "--port=8080",
            "--no-browser",
            "--NotebookApp.token=''",
            "--NotebookApp.password=''",
        ]
        run_command_as_user(command, user, env)
    else:
        raise ValueError(f"Unknown job type: {job_type}")


if __name__ == "__main__":
    try:
        logger.debug("Starting job execution...")
        main()
        logger.debug("Job executed successfully.")
    except Exception as e:
        logger.error(f"Error during job execution: {e}")
        raise
