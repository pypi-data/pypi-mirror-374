from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from dagtool.tasks.__abc import DAG, Context, Operator, TaskGroup, TaskModel


class CustomTask(BaseTask):
    """Custom Task model."""

    uses: Literal["custom_task"] = Field(description="A common task name.")
    name: str = Field(description="A common building function name.")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A mapping of parameters that want to pass to Custom Task model "
            "before build."
        ),
    )

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator | TaskGroup:
        """Build with Custom builder function.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.
        """
        ctx: Context = context or {}
        custom_tasks: dict[str, type[TaskModel]] = ctx["tasks"]
        if self.name not in custom_tasks:
            raise ValueError(
                f"Custom task need to pass to `tasks` argument, {self.name}, "
                f"first."
            )
        op: type[TaskModel] = custom_tasks[self.name]
        model: TaskModel = op.model_validate(self.params)
        return model.build(
            dag=dag,
            task_group=task_group,
            context=context | self.params,
        )
