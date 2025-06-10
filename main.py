import sys
import time
import asyncio
import threading
import warnings
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QThread

from indicators.OBI import OBISession
from utils.news import fetch_and_generate_signal

warnings.filterwarnings("ignore", category=RuntimeWarning)

SYMBOLS = ['ADAUSDT', 'POLUSDT', 'ETHUSDT', 'BTCUSDT', 'XRPUSDT', 'BNBUSDT']
state = {symbol: {'obi': 0.0, 'delta': 0.0} for symbol in SYMBOLS}


class OBIUpdateSignals(QObject):
    update_signal = pyqtSignal(str, float, float)


class NewsFetcher(QThread):
    result_ready = pyqtSignal(str)

    def run(self):
        try:
            signal = fetch_and_generate_signal()
        except Exception as e:
            print("News fetch error:", e)
            signal = "Error"
        self.result_ready.emit(signal)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 OBI Dashboard")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #121212; color: #f0f0f0; font-family: 'Segoe UI';")

        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(20, 20, 20, 20)

        # Top row: news and button
        top_row = QHBoxLayout()
        self.news_label = QLabel("News Signal: ⏳")
        self.news_label.setAlignment(Qt.AlignCenter)
        self.news_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.news_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #222;
                border-radius: 12px;
                padding: 10px 20px;
            }
        """)
        top_row.addWidget(self.news_label)

        self.refresh_button = QPushButton("🔄 Refresh News")
        self.refresh_button.clicked.connect(self.update_news_signal)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #1f1f1f;
                color: white;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 10px 18px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
        """)
        top_row.addWidget(self.refresh_button)
        layout.addLayout(top_row)

        # Grid for symbols
        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        layout.addLayout(self.grid)

        self.labels = {}
        for i, symbol in enumerate(SYMBOLS):
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    border-radius: 14px;
                    padding: 20px;
                    font-size: 15px;
                    border: 1px solid #333;
                }
            """)
            self.grid.addWidget(label, i // 3, i % 3)
            self.labels[symbol] = label

        self.signals = OBIUpdateSignals()
        self.signals.update_signal.connect(self.update_label_safe)

        # Timer
        self.news_timer = QTimer()
        self.news_timer.timeout.connect(self.update_news_signal)
        self.news_timer.start(15 * 60 * 1000)
        self.update_news_signal()

    def update_label_safe(self, symbol, obi, delta):
        state[symbol] = {'obi': obi, 'delta': delta}
        color = "#00ff00" if delta >= 0 else "#ff4c4c"
        html = f"""
            <div style='font-size:16px; font-weight:bold;'>{symbol.upper()}</div>
            <div style='margin-top:6px;'>OBI: <b>{obi:.4f}</b></div>
            <div style='color:{color}; font-weight:bold;'>Δ: {delta:.4f}</div>
        """
        self.labels[symbol].setText(html)

    def update_news_signal(self):
        self.news_label.setText("News Signal: ⏳")
        self.thread = NewsFetcher()
        self.thread.result_ready.connect(self.display_news_result)
        self.thread.start()

    def display_news_result(self, signal):
        color = {
            "BUY": "lime",
            "SELL": "tomato",
            "HOLD": "gold",
            "Error": "gray"
        }.get(signal, "white")
        self.news_label.setText(f"News Signal: {signal}")
        self.news_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: #222;
                border-radius: 12px;
                padding: 10px 20px;
            }}
        """)


app_instance = None

def wait_for_app_instance(timeout=5):
    waited = 0
    while waited < timeout:
        if app_instance is not None:
            return True
        time.sleep(0.1)
        waited += 0.1
    return False

def gui_callback(symbol, obi, delta):
    if app_instance:
        app_instance.signals.update_signal.emit(symbol, obi, delta)
        print(f"[GUI] Update {symbol} -> OBI: {obi:.4f}, Δ: {delta:.4f}")

async def start_obi_sessions(callback):
    sessions = [OBISession(symbol, callback=callback) for symbol in SYMBOLS]
    await asyncio.gather(*(s.run() for s in sessions))

def obi_thread():
    if not wait_for_app_instance():
        print("Timeout waiting for app_instance initialization!")
        return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_obi_sessions(gui_callback))

def start_gui():
    global app_instance
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/logo.png"))

    app_instance = MainWindow()
    app_instance.show()

    threading.Thread(target=obi_thread, daemon=True).start()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_gui()