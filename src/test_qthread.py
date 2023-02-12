import sys
import time
from typing import List

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class WorkerAbortedException(Exception):
    pass


class Worker(QObject):
    progressRange = Signal(int, int)
    progress = Signal(int)
    started = Signal()
    resultReady = Signal(int)
    finished = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self.mutex = QMutex()
        self.abort_requested_flag = False
        
    def is_abort_requested(self):
        with QMutexLocker(self.mutex):
            return self.abort_requested_flag

    def request_abort(self, abort: bool=True):
        print(f"Worker.request_abort - {abort}")
        with QMutexLocker(self.mutex):
            self.abort_requested_flag = abort
    
    @Slot()
    def do_multiply(self, values: List[int]):
        try:
            self.started.emit()
            self.request_abort(False)
            self.progressRange.emit(0, len(values))
            self.progress.emit(0)
            result = 1
            for idx, value in enumerate(values):
                time.sleep(1)
                if self.is_abort_requested():
                    raise WorkerAbortedException()
                result *= value
                self.progress.emit(idx + 1)
        except WorkerAbortedException:
            print("Worker.do_multiply - WorkerAbortedException")
        else:
            self.resultReady.emit(result)
        finally:
            self.finished.emit()

class Controller(QObject):
    operate = Signal(list)
    resultReady = Signal(int)
    stateChanged = Signal()
    progressRange = Signal(int, int)
    progress = Signal(int)
    
    def __init__(self) -> None:
        super().__init__()
        self.worker_thread = QThread()
        self.worker_thread.finished.connect(self.on_thread_finished)
        
        self.worker = Worker()
        self.worker.moveToThread(self.worker_thread)
        self.worker.resultReady.connect(self.handle_results)
        self.worker.started.connect(lambda: self.set_running(True))
        self.worker.finished.connect(lambda: self.set_running(False))
        self.worker.progressRange.connect(self.progressRange)
        self.worker.progress.connect(self.progress)
        
        self.operate.connect(self.worker.do_multiply)
        
        self.worker_thread.start()
        self.running_flag = False
        
    def is_running(self) -> bool:
        return self.running_flag
    
    def set_running(self, running: bool):
        self.running_flag = running
        self.stateChanged.emit()
        
    def start(self, values: List[int]):
        if self.is_running():
            print("Controller.start - Already running")
            return
        self.operate.emit(values)
        
    def stop(self):
        print("Controller.stop - Started")
        if not self.is_running():
            print("Controller.stop - Not running")
            return
        self.worker.request_abort(True)
        
    def stop_thread(self):
        print("Controller.stop_thread - Started")
        self.worker_thread.quit()
        self.worker_thread.wait()
        print("Controller.stop_thread - Finished")
        
    def on_thread_finished(self):
        print("Controller.on_thread_finished - Called")
        
    def handle_results(self, result: int):
        print(f"Controller.handle_result - {result}")
        self.resultReady.emit(result)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.counter = 0
        self.conter_label = QLabel("Start")
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("3,4,5")
        self.answer_label = QLabel("")
        self.start_button = QPushButton("START")
        self.start_button.pressed.connect(self.start)
        self.progress_bar = QProgressBar()
        self.stop_button = QPushButton("STOP")
        self.stop_button.pressed.connect(self.stop)
        
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(self.conter_label)
        layout.addWidget(self.input_edit)
        layout.addWidget(self.answer_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setCentralWidget(w)
        
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        
        self.controller = Controller()
        self.controller.progressRange.connect(self.set_progress_range)
        self.controller.progress.connect(self.set_progress)
        self.controller.stateChanged.connect(self.update_state)
        self.controller.resultReady.connect(self.on_result_ready)
        self.update_state()
        
    def closeEvent(self, event: QCloseEvent) -> None:
        self.stop_thread()
        return super().closeEvent(event)
        
    def set_progress(self, progress: int) -> None:
        self.progress_bar.setValue(progress)
        
    def set_progress_range(self, minimum: int, maximum: int) -> None:
        self.progress_bar.setRange(minimum, maximum)
        
    def update_state(self):
        self.start_button.setEnabled(not self.controller.is_running())
        self.stop_button.setEnabled(self.controller.is_running())
        
    def start(self):
        values = []
        s = self.input_edit.text()
        
        for token in s.split(","):
            try:
                value = int(token.strip())
                values.append(value)
            except:
                pass
        
        self.controller.start(values)
        self.answer_label.setText("?")
        
    def stop(self):
        print("MainWindow.stop - Started")
        self.controller.stop()
        
    def on_result_ready(self, result: int):
        print(f"MainWindow.on_result_ready - {result}")
        self.answer_label.setText(str(result))
        
    def stop_thread(self):
        print("MainWindow.stop_thread - Started")
        if self.controller.is_running():
            self.stop()
        self.controller.stop_thread()
        print("MainWindow.stop_thread - Finished")
        
    def recurring_timer(self):
        self.counter += 1
        self.conter_label.setText(f"Counter: {self.counter}")
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()