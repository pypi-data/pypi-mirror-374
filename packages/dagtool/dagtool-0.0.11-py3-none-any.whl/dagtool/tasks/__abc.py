from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict

try:
    from airflow.sdk.bases.operator import BaseOperator
    from airflow.sdk.definitions.dag import DAG
    from airflow.sdk.definitions.mappedoperator import MappedOperator
    from airflow.sdk.definitions.taskgroup import TaskGroup
except ImportError:
    from airflow.models.baseoperator import BaseOperator
    from airflow.models.dag import DAG
    from airflow.models.mappedoperator import MappedOperator
    from airflow.utils.task_group import TaskGroup

from airflow.configuration import conf as airflow_conf
from airflow.utils.trigger_rule import TriggerRule
from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import field_validator

if TYPE_CHECKING:
    from dagtool.conf import YamlConf

Operator = BaseOperator | MappedOperator


class Context(TypedDict):
    """Context type dict that wat generated from the Factory object before start
    building Airflow DAG from template config.
    """

    path: Path
    yaml_loader: YamlConf
    vars: dict[str, Any]
    tasks: dict[str, type[TaskModel]]
    operators: dict[str, type[Operator]]
    python_callers: dict[str, Callable]
    extras: dict[str, Any]


class ToolMixin(ABC):
    """Task Mixin Abstract class override the build method."""

    @abstractmethod
    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator | TaskGroup:
        """Build Any Airflow Task object. This method can return Operator or
        TaskGroup object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.

        Returns:
            Operator | TaskGroup: This method can return depend on building
                logic that already pass the DAG instance from the parent.
        """


class TaskModel(BaseModel, ToolMixin, ABC):
    """Task Model.

    This model will use to be the abstract model for any Task model that it want
    to use with a specific use case like CustomTask, etc.
    """


class BaseAirflowTaskModel(TaskModel, ABC):
    """Base Task model that represent Airflow Task object."""

    desc: str | None = Field(
        default=None,
        description=(
            "A Airflow task description that will pass to the `doc` argument."
        ),
    )
    upstream: list[str] = Field(
        default_factory=list,
        validate_default=True,
        description=(
            "A list of upstream task name or only task name of this task."
        ),
    )

    @field_validator(
        "upstream",
        mode="before",
        json_schema_input_type=str | list[str] | None,
    )
    def __prepare_upstream(cls, data: Any) -> Any:
        """Prepare upstream value that passing to validate with string value
        instead of list of string. This function will create list of this value.

        Args:
            data (Any): An any upstream data that pass before validating.
        """
        if data is None:
            return []
        elif data and isinstance(data, str):
            return [data]
        return data

    @property
    @abstractmethod
    def iden(self) -> str:
        """Task identity Abstract method for making represent task_id or group_id
        for Airflow object.
        """


class BaseTask(BaseAirflowTaskModel, ABC):
    """Base Task Model.

    This model will add necessary field that use with the Airflow BaseOperator
    object.
    """

    model_config = ConfigDict(use_enum_values=True)

    task: str = Field(description="A task name.")
    type: Literal["task"] = Field(default="task", description="A task type.")
    uses: str = Field(description="A tool type name.")
    trigger_rule: TriggerRule = Field(
        default=TriggerRule.ALL_SUCCESS,
        description=(
            "Task trigger rule. Read more detail, "
            "https://www.astronomer.io/blog/understanding-airflow-trigger-rules-comprehensive-visual-guide/"
        ),
    )
    owner: str | None = Field(default=None, description="An owner name.")
    email: str | list[str] | None = Field(
        default=None,
        description=(
            "the 'to' email address(es) used in email alerts. This can be a "
            "single email or multiple ones. Multiple addresses can be "
            "specified as a comma or semicolon separated string or by passing "
            "a list of strings."
        ),
    )
    email_on_failure: bool = Field(
        default_factory=partial(
            airflow_conf.getboolean,
            "email",
            "default_email_on_failure",
            fallback=True,
        ),
        description=(
            "Indicates whether email alerts should be sent when a task failed"
        ),
    )
    email_on_retry: bool = Field(
        default_factory=partial(
            airflow_conf.getboolean,
            "email",
            "default_email_on_retry",
            fallback=True,
        ),
    )
    depends_on_past: bool = Field(default=False)
    pool: str | None = Field(
        default=None,
        description=(
            "the slot pool this task should run in, slot pools are a "
            "way to limit concurrency for certain tasks."
        ),
    )
    pool_slots: int | None = Field(
        default=None,
        description=(
            "the number of pool slots this task should use (>= 1) "
            "Values less than 1 are not allowed."
        ),
    )
    retries: int | None = Field(default=None, description="A retry count.")
    retry_delay: dict[str, int] | None = Field(default=None)
    retry_exponential_backoff: bool = Field(default=False)
    executor_config: dict[str, Any] | None = Field(default=None)
    inlets: list[dict[str, Any] | str] = Field(
        default_factory=list,
        description="A list of inlets or inlet value.",
    )
    outlets: list[dict[str, Any] | str] = Field(
        default_factory=list,
        description="A list of outlets or outlet value.",
    )

    @abstractmethod
    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator | TaskGroup:
        """Build the Airflow Operator or TaskGroup object from this model
        field.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.
        """

    @property
    def iden(self) -> str:
        """Return the task field value for represent task_id in Airflow Task
        Instance.
        """
        return self.task

    def task_kwargs(self) -> dict[str, Any]:
        """Prepare the Airflow BaseOperator kwargs from BaseTask fields.

            This method will make key when any field was pass to model and do
        avoid if it is None or default value.
        """
        kws: dict[str, Any] = {
            "task_id": self.iden,
            "trigger_rule": self.trigger_rule,
            "retry_exponential_backoff": self.retry_exponential_backoff,
        }
        if self.desc:
            kws.update({"doc": self.desc})
        if self.inlets:
            kws.update({"inlets": self.inlets})
        if self.outlets:
            kws.update({"outlets": self.outlets})
        if self.executor_config:
            kws.update({"executor_config": self.executor_config})
        if self.retries:
            kws.update({"retries": self.retries})
        if self.retry_delay:
            kws.update({"retry_delay": self.retry_delay})
        if self.owner:
            kws.update({"owner": self.owner})
        if self.pool:
            kws.update({"pill": self.pool})
        if self.pool_slots:
            kws.update({"pool_slots": self.pool_slots})
        return kws
