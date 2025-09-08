from __future__ import annotations

from collections.abc import Sequence

try:
    from airflow.sdk.bases.operator import BaseOperator
except ImportError:
    from airflow.models.baseoperator import BaseOperator

from airflow.exceptions import AirflowException, AirflowSkipException
from airflow.utils.context import Context


class RaiseOperator(BaseOperator):
    """Airflow Raise Operator object that inherit from the Airflow BaseOperator
    object.
    """

    ui_color: str = "#ef3a25"
    inherits_from_empty_operator: bool = False
    template_fields: Sequence[str] = ("message",)

    def __init__(
        self,
        message: str | None,
        skipped: bool = False,
        **kwargs,
    ) -> None:
        """Main initialize."""
        super().__init__(**kwargs)
        self.skipped: bool = skipped
        self.message: str = (
            message or "Default message raise from Raise Operator."
        )

    def execute(self, context: Context) -> None:
        """Execute with Raise operator."""
        if self.skipped:
            raise AirflowSkipException(self.message)
        raise AirflowException(self.message)
