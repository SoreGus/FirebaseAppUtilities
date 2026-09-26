from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(object)
    finished = Signal()


class Worker(QRunnable):
    def __init__(
        self,
        fn: Callable[[], Any],
    ):
        super().__init__()
        self.fn = fn
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn()
        except Exception as error:
            self.signals.error.emit(error)
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class TaskHost:
    def __init__(self) -> None:
        self._thread_pool = QThreadPool.globalInstance()
        self._workers: set[Worker] = set()

    def run_task(
        self,
        fn: Callable[[], Any],
        *,
        on_result: Callable[[Any], None],
        on_error: Callable[[Exception], None],
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        worker = Worker(fn)
        self._workers.add(worker)

        worker.signals.result.connect(on_result)
        worker.signals.error.connect(on_error)

        def finished() -> None:
            self._workers.discard(worker)
            if on_finished:
                on_finished()

        worker.signals.finished.connect(finished)
        self._thread_pool.start(worker)
