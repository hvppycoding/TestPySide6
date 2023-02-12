import sys
import time
import traceback

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class WorkerKilledException(Exception):
    pass


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)


class Runner(QRunnable):
    def __init__(self, fn, *args, **kwargs) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exe_info()[:2]
            self.signals.error.emit(
                (exctype, value, traceback.format_exc())
            )
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()




class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.counter = 0
        
        layout = QVBoxLayout()
        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        b.pressed.connect(self.oh_no)
        layout.addWidget(self.l)
        layout.addWidget(b)
        
        w = QWidget()
        w.setLayout(layout)
        
        self.setCentralWidget(w)
        
        self.threadpool = QThreadPool()
        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        
    def print_output(self, s: str):
        print(s)
        
    def thread_complete(self):
        print("THREAD COMPLETE")
        
    def oh_no(self):
        def execute_this_fn(n: int):
            for _ in range(0, n):
                time.sleep(1)
            return "Done"
        
        worker = Runner(execute_this_fn, 10)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        self.threadpool.start(worker)
        
    def recurring_timer(self):
        self.counter += 1
        self.l.setText(f"Counter: {self.counter}")
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()