import sys
import time

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Worker(QRunnable):
    """
    Worker thread
    """
    
    def run(self):
        print("Thread start")
        time.sleep(5)
        print("Thread complete")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.threadpool = QThreadPool()
        print(
            f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads"
        )
        
        self.counter = 0
        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        b.pressed.connect(self.oh_no)
        
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(self.l)
        layout.addWidget(b)
        self.setCentralWidget(w)
        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        
    def oh_no(self):
        worker = Worker()
        self.threadpool.start(worker)
        
    def recurring_timer(self):
        self.counter += 1
        self.l.setText(f"Counter: {self.counter}")
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()