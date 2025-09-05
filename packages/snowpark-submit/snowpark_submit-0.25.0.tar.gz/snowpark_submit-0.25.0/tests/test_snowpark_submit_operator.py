#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import os
from unittest.mock import Mock

import pytest
from airflow.utils.context import Context
from snowflake.operators.snowpark_submit.snowpark_submit_operator import (
    SnowparkSubmitOperator,
    generate_service_name,
)

from snowflake.connector.config_manager import CONFIG_MANAGER

from .conftest import DEFAULT_TEST_CONNECTION_NAME


class TestSnowparkSubmitOperator:
    @classmethod
    def setup_class(cls):
        cls.tests_path = os.path.dirname(os.path.abspath(__file__))
        cls.project_root = os.path.dirname(cls.tests_path)

        cls.test_python_file = os.path.join(cls.tests_path, "resources/pyspark-test.py")
        cls.test_main_file = os.path.join(
            cls.tests_path, "resources/snowpark-submit-pyspark-example/main.py"
        )
        cls.test_jar_file = os.path.join(
            cls.tests_path,
            "resources/snowpark-submit-scala-example/target/original-scala-maven-example-0.1.0.jar",
        )

        snowpark_config = CONFIG_MANAGER["connections"][DEFAULT_TEST_CONNECTION_NAME]

        cls.connection_config = {
            "account": snowpark_config.get("account"),
            "host": snowpark_config.get("host"),
            "user": snowpark_config.get("user"),
            "password": snowpark_config.get("password"),
            "role": snowpark_config.get("role"),
            "warehouse": snowpark_config.get("warehouse"),
            "database": snowpark_config.get("database"),
            "schema": snowpark_config.get("schema"),
            "compute_pool": snowpark_config.get("compute_pool"),
        }

        mock_ti = Mock()
        mock_ti.xcom_push = Mock()
        cls.mock_context = Context()
        cls.mock_context["ti"] = mock_ti

    # ------------- UNIT TESTS -------------

    def test_missing_file_error(self):
        operator = SnowparkSubmitOperator(
            task_id="test_missing_file",
            file="/nonexistent/file.py",
            connections_config=self.connection_config,
        )

        with pytest.raises(FileNotFoundError, match="File not found"):
            operator.execute(self.mock_context)

    def test_comprehensive_command_building(self):
        # Test the command building
        pyspark_example_dir = os.path.join(
            self.tests_path, "resources/snowpark-submit-pyspark-example"
        )
        wheel_files_dir = os.path.join(pyspark_example_dir, "wheel-files")

        operator = SnowparkSubmitOperator(
            task_id="test_full_command",
            file=os.path.join(pyspark_example_dir, "main.py"),
            connections_config=self.connection_config,
            py_files=os.path.join(pyspark_example_dir, "utils.zip"),
            requirements_file=os.path.join(
                pyspark_example_dir, "test-requirements.txt"
            ),
            wheel_files=f"{wheel_files_dir}/access-1.1.9-py3-none-any.whl,{wheel_files_dir}/python_weather-2.1.0-py3-none-any.whl",
            init_script=os.path.join(pyspark_example_dir, "init.sh"),
            external_access_integrations="pypi_access_integration",
            comment="Test job with all dependency types",
            wait_for_completion=True,
            fail_on_error=True,
            application_args=["test_table"],
        )

        cmd = operator._build_command()

        assert "--py-files" in cmd
        assert os.path.join(pyspark_example_dir, "utils.zip") in cmd
        assert "--requirements-file" in cmd
        assert os.path.join(pyspark_example_dir, "test-requirements.txt") in cmd
        assert "--wheel-files" in cmd
        assert (
            f"{wheel_files_dir}/access-1.1.9-py3-none-any.whl,{wheel_files_dir}/python_weather-2.1.0-py3-none-any.whl"
            in cmd
        )
        assert "--init-script" in cmd
        assert os.path.join(pyspark_example_dir, "init.sh") in cmd
        assert "--external-access-integrations" in cmd
        assert "pypi_access_integration" in cmd
        assert "--wait-for-completion" in cmd
        assert "--comment" in cmd
        assert "Test job with all dependency types" in cmd
        assert os.path.join(pyspark_example_dir, "main.py") in cmd
        assert "test_table" in cmd

        assert operator.wait_for_completion is True
        assert operator.fail_on_error is True

    def test_unsupported_file_type_error(self):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
            temp_file_path = tf.name

        try:
            operator = SnowparkSubmitOperator(
                task_id="test_unsupported_file",
                file=temp_file_path,
                connections_config=self.connection_config,
            )

            with pytest.raises(
                ValueError,
                match="Unsupported file type: .txt. Only .py and .jar files are supported",
            ):
                operator.execute(self.mock_context)
        finally:
            os.unlink(temp_file_path)

    def test_jar_file_requires_main_class(self):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".jar", delete=False) as tf:
            temp_jar_path = tf.name

        try:
            operator = SnowparkSubmitOperator(
                task_id="test_jar_without_main_class",
                file=temp_jar_path,
                connections_config=self.connection_config,
            )

            with pytest.raises(
                ValueError, match="main_class is required for JAR files"
            ):
                operator.execute(self.mock_context)
        finally:
            os.unlink(temp_jar_path)

    def test_connections_config_validation(self):
        incomplete_config = {
            "account": "test_account",
            "host": "test_host.snowflakecomputing.com",
        }

        operator = SnowparkSubmitOperator(
            task_id="test_validation",
            file=self.test_python_file,
            connections_config=incomplete_config,
        )

        with pytest.raises(
            ValueError, match="Missing required Snowflake configuration parameters"
        ):
            operator.execute(self.mock_context)

    def test_service_name_generation(self):
        name1 = generate_service_name()
        name2 = generate_service_name()
        name3 = generate_service_name()

        assert name1.startswith("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_")
        assert name2.startswith("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_")
        assert name3.startswith("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_")

        assert name1 != name2 != name3, "Service names should be unique"
        assert len(name1) == len("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_") + 27

    # ------------- EXECUTION TESTS -------------
    # These tests require SPCS infrastructure
    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resources."
    )
    def test_operator_basic(self):
        operator = SnowparkSubmitOperator(
            task_id="test_cluster_basic",
            file=self.test_python_file,
            connections_config=self.connection_config,
        )

        result = operator.execute(self.mock_context)

        assert result is not None
        assert result["return_code"] == 0
        assert result["service_name"] is not None
        assert result["service_name"].startswith("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_")
        assert self.mock_context["ti"].xcom_push.call_count == 4
        calls = self.mock_context["ti"].xcom_push.call_args_list
        xcom_data = {call[1]["key"]: call[1]["value"] for call in calls}

        assert xcom_data["service_name"] == result["service_name"]
        assert xcom_data["return_code"] == 0

        stdout_content = result["stdout"]
        service_name = result["service_name"]
        assert (
            f"Job {service_name} has been submitted and running asynchronously in SPCS"
            in stdout_content
        ), f"Job submission to SPCS not confirmed for service {service_name}"

    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resource"
    )
    def test_custom_service_name(self):
        custom_name = "CUSTOM_TEST_SERVICE_12345"
        operator = SnowparkSubmitOperator(
            task_id="test_custom_service_name",
            file=self.test_python_file,
            connections_config=self.connection_config,
            service_name=custom_name,
        )

        result = operator.execute(self.mock_context)

        assert result is not None
        assert result["return_code"] == 0
        assert result["service_name"] == custom_name

        stdout_content = result["stdout"]
        assert (
            f"Job {custom_name} has been submitted and running asynchronously in SPCS"
            in stdout_content
        ), f"Job submission to SPCS not confirmed for custom service {custom_name}"

    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resource"
    )
    def test_properties_file_parameter(self):
        properties_file_path = os.path.join(
            self.tests_path, "resources/test_spark_properties.conf"
        )

        operator = SnowparkSubmitOperator(
            task_id="test_properties_file",
            file=self.test_python_file,
            connections_config=self.connection_config,
            properties_file=properties_file_path,
        )

        cmd = operator._build_command()
        assert "--properties-file" in cmd
        props_idx = cmd.index("--properties-file")
        assert cmd[props_idx + 1] == properties_file_path

        result = operator.execute(self.mock_context)

        assert result is not None
        assert result["return_code"] == 0

        stdout_content = result["stdout"]
        service_name = result["service_name"]
        assert (
            f"Job {service_name} has been submitted and running asynchronously in SPCS"
            in stdout_content
        )

    def test_missing_properties_file_error(self):
        operator = SnowparkSubmitOperator(
            task_id="test_missing_properties_file",
            file=self.test_python_file,
            connections_config=self.connection_config,
            properties_file="/nonexistent/spark-properties.conf",
        )

        with pytest.raises(FileNotFoundError, match="Properties file not found"):
            operator.execute(self.mock_context)

    # ------------- WAIT FOR COMPLETION EXECUTION TESTS -------------
    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resource"
    )
    def test_wait_for_completion_blocking_mode(self):
        operator = SnowparkSubmitOperator(
            task_id="test_blocking_mode",
            file=self.test_python_file,
            connections_config=self.connection_config,
            wait_for_completion=True,
            fail_on_error=True,
        )

        result = operator.execute(self.mock_context)

        assert result is not None
        assert result["return_code"] == 0
        assert result["service_name"] is not None
        assert result["service_name"].startswith("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_")

        stdout_content = result["stdout"]
        service_name = result["service_name"]

        assert (
            "Workload Status: DONE" in stdout_content
        ), f"Job completion not confirmed in blocking mode for service {service_name}"

    # @pytest.mark.skip(reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resource")
    def test_wait_for_completion_scala_jar(self):
        operator = SnowparkSubmitOperator(
            task_id="test_blocking_scala_jar",
            file=self.test_jar_file,
            main_class="com.example.SnowparkConnectApp",
            application_args=["TEST_SCALA_OUTPUT_TABLE"],
            connections_config=self.connection_config,
            comment="Scala test execution in blocking mode",
            wait_for_completion=True,
            fail_on_error=True,
        )

        result = operator.execute(self.mock_context)

        assert result is not None
        assert result["return_code"] == 0
        assert result["service_name"] is not None
        assert result["service_name"].startswith("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_")

        stdout_content = result["stdout"]
        service_name = result["service_name"]

        assert (
            "Workload Status: DONE" in stdout_content
        ), f"Scala JAR job completion not confirmed in blocking mode for service {service_name}"

    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resource"
    )
    def test_operator_with_pyfiles(self, pyspark_utils_zip):
        operator = SnowparkSubmitOperator(
            task_id="test_cluster_pyfiles",
            file=self.test_main_file,
            connections_config=self.connection_config,
            py_files=str(pyspark_utils_zip.resolve()),
            application_args=["test_pyfiles_table"],
            wait_for_completion=True,
        )

        result = operator.execute(self.mock_context)

        assert result is not None
        assert result["return_code"] == 0
        assert result["service_name"] is not None
        assert result["service_name"].startswith("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_")

        stdout_content = result["stdout"]
        service_name = result["service_name"]

        assert (
            "Workload Status: DONE" in stdout_content
        ), f"Job completion not confirmed in blocking mode for service {service_name}"

    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resource"
    )
    def test_wait_for_completion_job_failure(self):
        failing_python_file = os.path.join(
            self.tests_path, "resources/pyspark-test-failing.py"
        )

        operator = SnowparkSubmitOperator(
            task_id="test_job_failure",
            file=failing_python_file,
            connections_config=self.connection_config,
            wait_for_completion=True,
            fail_on_error=True,
        )

        with pytest.raises(Exception, match="Spark job failed with status: FAILED"):
            operator.execute(self.mock_context)

    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resource"
    )
    def test_wait_for_completion_job_failure_tolerant(self):
        failing_python_file = os.path.join(
            self.tests_path, "resources/pyspark-test-failing.py"
        )

        operator = SnowparkSubmitOperator(
            task_id="test_job_failure_tolerant",
            file=failing_python_file,
            connections_config=self.connection_config,
            wait_for_completion=True,
            fail_on_error=False,  # Shouldnt cause Airflow task to fail
        )

        result = operator.execute(self.mock_context)

        assert result is not None
        assert result["return_code"] == 0
        assert result["service_name"] is not None

        stdout_content = result["stdout"]
        assert (
            "Workload Status: FAILED" in stdout_content
        ), "Expected to see job failure status in blocking mode"
