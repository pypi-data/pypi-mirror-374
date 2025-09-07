from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from dagtool.plugins.operators.debug import DebugOperator
from dagtool.plugins.operators.error import RaiseOperator
from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from dagtool.tasks.__abc import DAG, Context, Operator, TaskGroup


class RaiseTask(BaseTask):
    """Raise Task model."""

    uses: Literal["raise"]
    message: str | None = Field(default=None)
    skipped: bool = False

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Raise Operator object."""
        return RaiseOperator(
            message=self.message,
            skipped=self.skipped,
            dag=dag,
            task_group=task_group,
            **self.task_kwargs(),
        )


class DebugTask(BaseTask):
    """Debug Task model that inherit from Operator task."""

    uses: Literal["debug"]
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="A parameters that want to logging.",
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Debug Operator object."""
        return DebugOperator(
            task_group=task_group,
            dag=dag,
            debug=self.params,
            **self.task_kwargs(),
        )
