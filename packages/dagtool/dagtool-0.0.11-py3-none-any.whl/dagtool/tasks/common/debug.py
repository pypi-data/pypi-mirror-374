from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from dagtool.plugins.common.operators.debug import DebugOperator
from dagtool.plugins.common.operators.error import RaiseOperator
from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from dagtool.tasks.__abc import DAG, Context, Operator, TaskGroup


class RaiseTask(BaseTask):
    """Raise Task model."""

    uses: Literal["raise"] = Field(description="A raise task name.")
    message: str | None = Field(default=None)
    skipped: bool = Field(default=False)

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Raise Operator object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.
        """
        return RaiseOperator(
            message=self.message,
            skipped=self.skipped,
            dag=dag,
            task_group=task_group,
            **self.task_kwargs(),
        )


class DebugTask(BaseTask):
    """Debug Task model."""

    uses: Literal["debug"] = Field(description="A debug task name.")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="A parameters that want to logging.",
    )

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Debug Operator object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.
        """
        return DebugOperator(
            task_group=task_group,
            dag=dag,
            debug=self.params,
            **self.task_kwargs(),
        )
