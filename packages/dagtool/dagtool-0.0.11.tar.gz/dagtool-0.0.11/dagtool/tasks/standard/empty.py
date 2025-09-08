from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field

try:
    from airflow.providers.standard.operators.empty import EmptyOperator
except ImportError:
    from airflow.operators.empty import EmptyOperator

from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from dagtool.tasks.__abc import DAG, Context, Operator, TaskGroup


class EmptyTask(BaseTask):
    """Empty Task model.

    This task model will build the Airflow EmptyOperator instance only.
    """

    uses: Literal["empty"] = Field(description="An empty task name.")

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Empty Operator object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.

        Returns:
            Operator: An Airflow EmptyOperator instance.
        """
        return EmptyOperator(
            dag=dag,
            task_group=task_group,
            **self.task_kwargs(),
        )
