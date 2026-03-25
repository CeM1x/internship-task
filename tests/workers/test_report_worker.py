import asyncio

import pytest


def test_generate_52_weeks_reports(monkeypatch):
    calls = []

    class FakeActor:
        def send(self, *args):
            calls.append(args)

    # подменяем generate_week_report на фейковый актор
    monkeypatch.setattr("app.workers.reports.generate_week_report", FakeActor())

    from app.workers.reports import generate_52_weeks_reports

    generate_52_weeks_reports()

    assert len(calls) == 52


@pytest.mark.asyncio
async def test_generate_week_report(monkeypatch):
    called = {"value": False}

    async def fake_run(start, end):
        called["value"] = True

    monkeypatch.setattr("app.workers.reports._run_week_report", fake_run)

    from app.workers.reports import generate_week_report

    generate_week_report("2024-01-01", "2024-01-08")

    await asyncio.sleep(0)

    assert called["value"] is True
