import asyncio
import logging
import os
from datetime import date, timedelta

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.db.session import async_session_maker
from app.services.report_service import ReportService

logger = logging.getLogger("reports_worker")


def setup_broker():
    redis_url = os.getenv("DRAMATIQ_BROKER", "redis://redis:6379/0")
    dramatiq.set_broker(RedisBroker(url=redis_url))


# В продакшене брокер включаем
if os.getenv("ENV") != "test":
    setup_broker()


@dramatiq.actor
def generate_52_weeks_reports():
    today = date.today()
    logger.info("Начинаю генерацию отчётов за 52 недели")

    for i in range(52):
        week_end = today - timedelta(weeks=i)
        week_start = week_end - timedelta(days=7)

        generate_week_report.send(week_start.isoformat(), week_end.isoformat())

    logger.info("Все задачи отправлены в очередь")


async def _run_week_report(week_start: str, week_end: str):
    async with async_session_maker() as session:
        service = ReportService(session)
        await service.build_week_report(week_start, week_end)
        logger.info(f"Отчет за {week_start} - {week_end} создан")


@dramatiq.actor
def generate_week_report(week_start: str, week_end: str):
    """
    Важно: НЕ используем asyncio.run().
    Просто создаём таск в текущем event loop.
    """
    loop = asyncio.get_event_loop()
    loop.create_task(_run_week_report(week_start, week_end))
