from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

import db
from db import SessionLocal
from db.models import ScheduledTask, Log

scheduler = BackgroundScheduler()
_notify: Callable[[str], Any] | None = None


def set_notify_callback(cb: Callable[[str], Any] | None) -> None:
    global _notify
    _notify = cb


def _notify_user(message: str) -> None:
    if _notify:
        try:
            _notify(message)
        except Exception:  # pragma: no cover - notification is best effort
            logging.exception("Notification callback failed")


def _run_task(task_id: int) -> None:
    with SessionLocal() as session:
        task = session.get(ScheduledTask, task_id)
        if not task:
            return
        try:
            result = f"Executed {task.name}"
        except Exception as e:  # pragma: no cover - placeholder execution
            result = f"Error running {task.name}: {e}"
        session.add(Log(created=datetime.utcnow(), level="INFO", message=result))
        session.commit()
        _notify_user(result)


def load_tasks() -> None:
    with SessionLocal() as session:
        tasks = session.query(ScheduledTask).all()
    for t in tasks:
        if t.status != "disabled":
            scheduler.add_job(
                _run_task,
                trigger="date",
                run_date=t.scheduled_for,
                id=str(t.id),
                args=[t.id],
            )


def add_task(name: str, when: datetime) -> int:
    with SessionLocal() as session:
        task = ScheduledTask(name=name, scheduled_for=when, status="active")
        session.add(task)
        session.commit()
        scheduler.add_job(
            _run_task,
            trigger="date",
            run_date=task.scheduled_for,
            id=str(task.id),
            args=[task.id],
        )
        return task.id


def remove_task(task_id: int) -> None:
    try:
        scheduler.remove_job(str(task_id))
    except JobLookupError:
        pass
    with SessionLocal() as session:
        task = session.get(ScheduledTask, task_id)
        if task:
            session.delete(task)
            session.commit()


def toggle_task(task_id: int) -> None:
    with SessionLocal() as session:
        task = session.get(ScheduledTask, task_id)
        if not task:
            return
        if task.status == "active":
            task.status = "disabled"
            try:
                scheduler.remove_job(str(task.id))
            except JobLookupError:
                pass
        else:
            task.status = "active"
            scheduler.add_job(
                _run_task,
                trigger="date",
                run_date=task.scheduled_for,
                id=str(task.id),
                args=[task.id],
            )
        session.commit()


scheduler.start()
load_tasks()
