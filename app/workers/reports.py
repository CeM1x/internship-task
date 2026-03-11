import asyncio
import logging
import os
from datetime import date, timedelta

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.db.session import async_session_maker
from app.services.report_service import ReportService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("reports_worker")


redis_url = os.getenv("DRAMATIQ_BROKER", "redis://redis:6379/0")
dramatiq.set_broker(RedisBroker(url=redis_url))


@dramatiq.actor
def generate_52_weeks_reports():
    today = date.today()
    logger.info("Начинаю генерацию отчётов за 52 недели")
    for i in range(52):
        week_end = today - timedelta(weeks=i)
        week_start = week_end - timedelta(days=7)

        generate_week_report.send(week_start.isoformat(), week_end.isoformat())
    logger.info("Все задачи отправлены в очередь")


@dramatiq.actor
def generate_week_report(week_start: str, week_end: str):
    async def _run():
        async with async_session_maker() as session:
            service = ReportService(session)
            await service.build_week_report(
                week_start.isoformat(),
                week_end.isoformat(),
            )
            logger.info(f"Отчет за {week_start} - {week_end} создан")

    asyncio.run(_run())
