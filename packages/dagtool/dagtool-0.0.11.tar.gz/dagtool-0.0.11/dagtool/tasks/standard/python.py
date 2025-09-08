from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

try:
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:
    from airflow.operators.python import PythonOperator

from pydantic import Field

from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from dagtool.tasks.__abc import DAG, Context, Operator, TaskGroup


class PythonTask(BaseTask):
    """Python Task model."""

    uses: Literal["python"] = Field(description="A Python task name.")
    caller: str = Field(
        description=(
            "A Python function name that already set on the `python_callers` "
            "parameter."
        )
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="A parameters that will pass to the `op_kwargs` argument.",
    )

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Python Operator object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.

        Returns:
            Operator: An Airflow PythonOperator instance.
        """
        ctx: dict[str, Any] = context or {}
        python_callers: dict[str, Any] = ctx["python_callers"]
        if self.caller not in python_callers:
            raise ValueError(
                f"Python task need to pass python callers function, "
                f"{self.caller}, first."
            )
        return PythonOperator(
            dag=dag,
            task_group=task_group,
            python_callable=python_callers[self.caller],
            op_kwargs=self.params,
            **self.task_kwargs(),
        )
