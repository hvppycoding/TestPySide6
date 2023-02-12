import sys
import time

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class WorkerKilledException(Exception):
    pass


class WorkerSignals(QObject):
    progress = Signal(int)


class Runner(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals = WorkerSignals()
        self.is_killed = False
    
    def run(self):
        try:
            total_n = 100
            for n in range(total_n):
                if self.is_killed:
                    raise WorkerKilledException
                progress = 100 * (n + 1) // total_n
                print(f"Worker.run::{QThread.currentThread()}: {progress}")
                self.signals.progress.emit(progress)
                time.sleep(0.1)
        except WorkerKilledException:
            pass
        
    def kill(self):
        print(f"Runner.kill::{QThread.currentThread()}")
        self.is_killed = True


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.threadpool = QThreadPool()
        print(
            f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads"
        )
        
        self.progress = QProgressBar()
        btn_start = QPushButton("START!")
        btn_kill = QPushButton("STOP!")

        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(self.progress)
        layout.addWidget(btn_start)
        layout.addWidget(btn_kill)
        self.setCentralWidget(w)
        
        self.runner = Runner()
        
        btn_start.pressed.connect(self.execute)
        self.runner.signals.progress.connect(self.update_progress)
        btn_kill.pressed.connect(self.runner.kill)

    def execute(self) -> None:
        self.threadpool.start(self.runner)
        
    def update_progress(self, progress: int):
        print(f"MainWindow.update_progress::{QThread.currentThread()}: {progress}")
        self.progress.setValue(progress)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()