from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, cast

try:
    from airflow.sdk.bases.operator import BaseOperator
except ImportError:
    from airflow.models.baseoperator import BaseOperator

from airflow.utils.context import Context


class DebugOperator(BaseOperator):
    """Operator that does literally nothing.

    It can be used to group tasks in a DAG.
    The task is evaluated by the scheduler but never processed by the executor.
    """

    ui_color: str = "#fcf5a2"
    inherits_from_empty_operator: bool = False
    template_fields: Sequence[str] = ("debug",)

    def __init__(self, debug: dict[str, Any], **kwargs) -> None:
        super().__init__(**kwargs)
        self.debug: dict[str, Any] = debug

    def execute(self, context: Context) -> None:
        """Debug Operator execute method that only show parameters that passing
        from the template config.

        Args:
            context (AirflowContext): An Airflow Context object.
        """
        self.log.info("Start DEBUG Parameters:")
        for k, v in self.debug.items():
            self.log.info(f"> {k}: {v}")

        self.log.info("Start DEBUG Context:")
        ctx: Context = cast(Context, dict(context))
        self.log.info(json.dumps(ctx, indent=2, default=str))
