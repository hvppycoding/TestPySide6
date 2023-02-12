import sys
import time

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class WorkerSignals(QObject):
    progress = Signal(int)

class Worker(QRunnable):
    """
    Worker thread
    """
    def __init__(self) -> None:
        super().__init__()
        self.signals = WorkerSignals()
    
    def run(self):
        total_n = 100
        for n in range(total_n):
            progress = 100 * (n + 1) // total_n
            print(f"Worker.run::{QThread.currentThread()}: {progress}")
            self.signals.progress.emit(progress)
            time.sleep(0.1)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.threadpool = QThreadPool()
        print(
            f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads"
        )
        
        self.progress = QProgressBar()
        b = QPushButton("START!")
        b.pressed.connect(self.execute)
        
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(self.progress)
        layout.addWidget(b)
        self.setCentralWidget(w)

    def execute(self) -> None:
        worker = Worker()
        worker.signals.progress.connect(self.update_progress)
        self.threadpool.start(worker)
        
    def update_progress(self, progress: int):
        print(f"MainWindow.update_progress::{QThread.currentThread()}: {progress}")
        self.progress.setValue(progress)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()