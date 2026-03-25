from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class WeeklyReport(BaseModel):
    week_start: date
    week_end: date
    registered_users: int
    deposit_users_including_rollbacked: int
    deposit_users_without_rollback: int
    deposit_amount_usd: Decimal
    withdraw_amount_usd: Decimal
    transactions_total: int
    transactions_without_rollback: int

    model_config = {"json_encoders": {Decimal: lambda v: float(v)}}
