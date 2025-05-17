import sys
import os
import time
import webbrowser
import glob
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QEasingCurve, QPropertyAnimation
from PyQt5.QtGui import QColor, QFont, QPalette


from html_fetcher import fetch_and_save_html
from processor.html_parser import extract_text_from_html
from summarizer import (
    clean_and_structure_full_text,
    clean_and_structure_ocr_text,
    merge_and_deduplicate_text,
    generate_excel_data_from_merged_text
)
from screenshot_scroller import take_screenshot
from ocr_extractor import extract_text_from_screenshot
from excel_builder import save_product_table_to_excel

class Worker(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        start_time = time.time()
        try:
            self.log.emit("\n🔗 Fetching HTML...")
            html_path = fetch_and_save_html(self.url)
            base_name = os.path.basename(html_path).replace(".html", "")

            self.log.emit("\n📄 Extracting clean text from HTML...")
            clean_text = extract_text_from_html(html_path)
            parsed_path = os.path.join("outputs", "summaries", f"{base_name}_parsed_text.txt")
            with open(parsed_path, "w", encoding="utf-8") as f:
                f.write(clean_text)
            self.log.emit(f"📝 Parsed text saved to: {parsed_path}")

            self.log.emit("\n🧠 Cleaning and structuring full text with LM Labs...")
            formatted_text = clean_and_structure_full_text(clean_text)
            formatted_path = os.path.join("outputs", "summaries", f"{base_name}_formatted.txt")
            with open(formatted_path, "w", encoding="utf-8") as f:
                f.write(formatted_text)
            self.log.emit(f"\n✅ Final structured output saved to: {formatted_path}")

            self.log.emit("\n📸 Taking full-page screenshot...")
            screenshot_path = take_screenshot(self.url)
            self.log.emit(f"🖼️ Screenshot saved to: {screenshot_path}")

            self.log.emit("\n🔍 Running OCR on the screenshot...")
            ocr_file_path, ocr_text = extract_text_from_screenshot(screenshot_path)
            self.log.emit(f"📄 OCR raw text saved to: {ocr_file_path}")

            self.log.emit("\n🧹 Cleaning and structuring OCR text with LM Labs...")
            formatted_ocr_text = clean_and_structure_full_text(ocr_text)
            ocr_base = os.path.basename(screenshot_path).replace(".png", "")
            formatted_ocr_path = os.path.join("outputs", "summaries", f"{ocr_base}_ocr_cleaned.txt")
            with open(formatted_ocr_path, "w", encoding="utf-8") as f:
                f.write(formatted_ocr_text)
            self.log.emit(f"\n✅ Final structured OCR output saved to: {formatted_ocr_path}")

            self.log.emit("\n🔁 Merging HTML + OCR cleaned text...")
            with open(formatted_path, "r", encoding="utf-8") as f:
                html_cleaned = f.read()
            with open(formatted_ocr_path, "r", encoding="utf-8") as f:
                ocr_cleaned = f.read()
            merged_text = merge_and_deduplicate_text(html_cleaned, ocr_cleaned)
            merged_path = os.path.join("outputs", "summaries", f"{base_name}_merged_cleaned.txt")
            with open(merged_path, "w", encoding="utf-8") as f:
                f.write(merged_text)
            self.log.emit(f"\n✅ Merged, deduplicated final text saved to: {merged_path}")

            self.log.emit("\n📊 Generating intelligent Excel via LM Labs...")
            with open(merged_path, "r", encoding="utf-8") as f:
                merged_data = f.read()
            excel_data = generate_excel_data_from_merged_text(merged_data)
            excel_output_path = os.path.join("outputs", "excels", f"{base_name}_final.xlsx")
            save_product_table_to_excel(excel_data, excel_output_path)
            self.log.emit(f"\n✅ Final Excel saved to: {excel_output_path}")

            self.log.emit("\n🧹 Cleaning up temporary files...")
            for file in glob.glob("outputs/html/*.html"):
                os.remove(file)
            for file in glob.glob("outputs/screenshots/*.png"):
                os.remove(file)
            for file in glob.glob("outputs/summaries/*.txt"):
                os.remove(file)
            self.log.emit("✅ All intermediate files removed.")

            elapsed = time.time() - start_time
            mins, secs = divmod(elapsed, 60)
            self.log.emit(f"\n⏱️ Time Elapsed: {int(mins)} min {int(secs)} sec")
            self.finished.emit(excel_output_path)

        except Exception as e:
            self.log.emit(f"❌ Error: {str(e)}")
            self.finished.emit("ERROR")

class IngestAI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IngestAI ✨")
        self.setGeometry(200, 200, 900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 8px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QLineEdit, QTextEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 6px;
                color: white;
            }
            QLabel {
                font-weight: bold;
                margin-top: 6px;
            }
        """)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL to scrape...")
        layout.addWidget(QLabel("🌐 URL:"))
        layout.addWidget(self.url_input)

        btn_row = QHBoxLayout()
        self.run_button = QPushButton("▶️ Run Smart Extract")
        self.run_button.clicked.connect(self.run_process)
        btn_row.addWidget(self.run_button)

        self.stop_button = QPushButton("⛔ Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_process)
        btn_row.addWidget(self.stop_button)

        self.open_button = QPushButton("📂 Open Excel")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self.open_excel_file)
        btn_row.addWidget(self.open_button)

        self.timer_label = QLabel("⏱ 00:00")
        btn_row.addWidget(self.timer_label)
        layout.addLayout(btn_row)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(QLabel("📜 Main Logs:"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.start_time = None

    def run_process(self):
        url = self.url_input.text().strip()
        if not url:
            self.log_output.append("⚠️ Please enter a valid URL.")
            return

        self.log_output.clear()
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.open_button.setEnabled(False)
        self.worker = Worker(url)
        self.worker.log.connect(self.log_output.append)
        self.worker.finished.connect(self.on_done)
        self.start_time = time.time()
        self.timer.start(1000)
        self.worker.start()

    def stop_process(self):
        if self.worker:
            self.worker.terminate()
            self.log_output.append("⛔ Process manually stopped.")
            self.timer.stop()
            self.stop_button.setEnabled(False)
            self.run_button.setEnabled(True)

    def update_timer(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.timer_label.setText(f"⏱ {mins:02}:{secs:02}")

    def on_done(self, path):
        self.timer.stop()
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if path != "ERROR":
            self.log_output.append(f"\n📂 Done. File saved: {path}")
            self.open_button.setEnabled(True)
            self.excel_path = path
        else:
            self.log_output.append("❌ Process failed.")

    def open_excel_file(self):
        if hasattr(self, "excel_path") and os.path.exists(self.excel_path):
            webbrowser.open(self.excel_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IngestAI()
    window.show()
    sys.exit(app.exec_())