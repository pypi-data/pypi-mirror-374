#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import argparse
import os
from typing import Callable

from snowflake.snowpark_submit.cluster_mode.job_runner import JobRunner


class SparkConnectJobRunner(JobRunner):
    def __init__(
        self,
        args: argparse.Namespace,
        generate_spark_cmd_args: Callable[[argparse.Namespace], list[str]],
    ) -> None:
        super().__init__(
            args,
            generate_spark_cmd_args,
            client_working_dir="/app/",
            temp_stage_mount_dir="/app/client-src/",
            current_dir=os.path.dirname(os.path.abspath(__file__)),
        )

    def _generate_client_container_args(
        self, client_src_zip_file_path: str
    ) -> list[str]:
        args = []
        if client_src_zip_file_path:
            args.extend(["--zip", client_src_zip_file_path])
        args.append(" ".join(self.generate_spark_cmd_args(self.args)))
        return args

    def _get_image_tag(self, env_var_name: str) -> str:
        """
        First, it checks the provided parameter, then checks the environment variable, then defaults to "latest".
        """

        from_param = self.args.snowpark_connect_version
        from_env = os.getenv(env_var_name)

        if from_param == "latest" or (not from_param and not from_env):
            return "latest"
        if not from_param:
            return from_env
        import re

        if re.match(r"^\d+\.\d+\.\d+$", from_param):
            return from_param
        else:
            raise Exception("Incorrect snowpark-connect-version parameter value.")

    def _server_image_path_sys_registry(self) -> str:
        version_tag = self._get_image_tag("SNOWFLAKE_SYSTEM_REGISTRY_SERVER_IMAGE_TAG")
        return f"/snowflake/images/snowflake_images/spark_connect_for_snowpark_server:{version_tag}"

    def _client_image_path_sys_registry(self) -> str:
        version_tag = self._get_image_tag("SNOWFLAKE_SYSTEM_REGISTRY_CLIENT_IMAGE_TAG")
        return f"/snowflake/images/snowflake_images/spark_connect_for_snowpark_client_{self.client_app_language}:{version_tag}"

    def _client_image_name_override(self) -> str:
        return f"snowpark-connect-client-{self.client_app_language}:latest"

    def _server_image_name_override(self) -> str:
        return "snowpark-connect-server:latest"

    def _add_additional_jars_to_classpath(self) -> None:
        # spark-connect-client-jvm_2.12-3.5.3.jar is copied in the docker image.
        self._add_class_paths(
            ["/app/spark_lib/spark-connect-client-jvm_2.12-3.5.3.jar"]
        )

    def _use_system_registry(self) -> bool:
        return os.getenv("SNOWFLAKE_USE_SYSTEM_REGISTRY", "True").lower() == "true"

    def _override_args(self) -> None:

        pass
