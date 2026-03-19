from datetime import date

from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.report.weekly import WeeklyReport


class ReportService:
    def __init__(self, session):
        self.session = session
        self.users = UserRepository(session)
        self.tx = TransactionRepository(session)

    async def build_week_report(self, week_start: date, week_end: date) -> WeeklyReport:
        return WeeklyReport(
            week_start=week_start,
            week_end=week_end,
            registered_users=await self.users.get_registered_users_count(week_start, week_end),
            deposit_users_including_rollbacked=await self.users.get_registered_and_deposit_users_count(
                week_start, week_end
            ),
            deposit_users_without_rollback=await self.users.get_registered_and_not_rollbacked_deposit_users_count(
                week_start, week_end
            ),
            deposit_amount_usd=await self.tx.get_not_rollbacked_deposit_amount_in_USD(week_start, week_end),
            withdraw_amount_usd=await self.tx.get_not_rollbacked_withdraw_amount(week_start, week_end),
            transactions_total=await self.tx.get_transactions_count(week_start, week_end),
            transactions_without_rollback=await self.tx.get_not_rollbacked_transactions_count(
                week_start, week_end
            ),
        )
