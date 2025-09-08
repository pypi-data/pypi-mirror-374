from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from dagtool.tasks.__abc import DAG, Context, Operator, TaskGroup


class OperatorTask(BaseTask):
    """Operator Task model."""

    uses: Literal["operator"] = Field(description="An operator task name.")
    name: str = Field(
        description="An Airflow operator that import from external provider.",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A mapping of parameters that want to pass to Airflow Operator"
        ),
    )

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build the Airflow Operator instance that match with name and operator
        mapping.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.
        """
        ctx: Context = context or {}
        custom_opts: dict[str, type[Operator]] = ctx["operators"]
        if self.name not in custom_opts:
            raise ValueError(
                f"Operator need to pass to `operators` argument, "
                f"{self.name}, first."
            )
        op: type[Operator] = custom_opts[self.name]
        return op(
            dag=dag,
            task_group=task_group,
            **(self.params | self.task_kwargs()),
        )
