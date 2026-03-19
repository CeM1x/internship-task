from datetime import date, timedelta

from app.schemas.report.weekly import WeeklyReport
from app.services.report_service import ReportService


class ReportAnalysisService:
    def __init__(self, session):
        self.session = session
        self.report_service = ReportService(session)

    async def build_52_weeks_analysis(self) -> list[WeeklyReport]:
        today = date.today()
        results: list[WeeklyReport] = []

        for i in range(52):
            week_end = today - timedelta(weeks=i)
            week_start = week_end - timedelta(days=7)

            report = await self.report_service.build_week_report(week_start, week_end)

            if any(
                [
                    report.registered_users,
                    report.deposit_users_including_rollbacked,
                    report.deposit_users_without_rollback,
                    report.deposit_amount_usd,
                    report.withdraw_amount_usd,
                    report.transactions_total,
                    report.transactions_without_rollback,
                ]
            ):
                results.append(report)

        return results
