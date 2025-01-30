import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import markdown

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")

def set_api_key(new_key):
    """Update API key and configure genai."""
    global api_key
    api_key = new_key
    genai.configure(api_key=api_key)

set_api_key(api_key)  # Set initial API key

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

full_prompt = """
You are Sutrabot, a wise, pragmatic mentor offering practical advice. You provide clear, actionable, step-by-step solutions to life’s challenges. While grounded in modern problem-solving, you occasionally draw upon wisdom from the Vedas, Bhagavad Gita, and Chanakya Niti to provide deeper insights.
"""

def generate(input_text):
    """Generate a response from the AI."""
    prompt_with_input = f"{full_prompt}\ninput: {input_text}\noutput: "
    response = model.generate_content([prompt_with_input])
    return response.text

class WorkerThread(QThread):
    """Thread for handling API requests."""
    finished = pyqtSignal(str)

    def __init__(self, input_text):
        super().__init__()
        self.input_text = input_text

    def run(self):
        response = generate(self.input_text)
        self.finished.emit(response)

class SutrabotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sutrabot: Your Wise Guide")
        self.setGeometry(200, 200, 600, 500)
        self.setStyleSheet("""
            background-color: #1A1A1A;
            color: white;
            font-family: Arial, sans-serif;
            border-radius: 15px;
        """)

        layout = QVBoxLayout()

        # API Key Input
        self.api_dropdown = QComboBox(self)
        self.api_dropdown.setEditable(True)
        self.api_dropdown.setPlaceholderText("Enter your API key here...")
        self.api_dropdown.setStyleSheet("""
            font-size: 14px;
            background-color: #333;
            color: white;
            padding: 8px;
            border-radius: 10px;
        """)
        self.api_dropdown.currentTextChanged.connect(lambda key: set_api_key(key.strip()))
        layout.addWidget(self.api_dropdown)

        # Title
        self.title_label = QLabel("Sutrabot: Your Wise Guide")
        self.title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #4CAF50; 
            padding: 10px;
            text-align: center;
        """)
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        # Scrollable Chat Log
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)
        self.chat_log.setStyleSheet("""
            font-size: 14px; 
            background-color: #222;
            color: white;
            padding: 10px;
            border-radius: 10px;
        """)
        self.scroll_area.setWidget(self.chat_log)
        layout.addWidget(self.scroll_area)

        # Input field
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Ask a question...")
        self.input_field.setStyleSheet("""
            font-size: 16px;
            padding: 10px;
            background-color: #333;
            color: white;
            border-radius: 10px;
        """)
        layout.addWidget(self.input_field)

        # Ask Button
        self.submit_button = QPushButton("Ask", self)
        self.submit_button.setStyleSheet("""
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            border-radius: 10px;
            transition: background-color 0.3s ease;
        """)
        self.submit_button.setFixedSize(120, 40)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

        # Loading Label
        self.loading_label = QLabel("⌛ Loading...")
        self.loading_label.setStyleSheet("""
            font-size: 18px;
            color: #FF9800;
            padding: 10px;
            text-align: center;
            font-weight: bold;
        """)
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def on_submit(self):
        """Handle button click to get response."""
        user_input = self.input_field.text().strip()
        if user_input:
            self.loading_label.setVisible(True)
            self.submit_button.setEnabled(False)

            # Add user input to chat log
            self.chat_log.append(f"<b>User:</b> {user_input}")

            # Start background thread for API request
            self.worker_thread = WorkerThread(user_input)
            self.worker_thread.finished.connect(self.on_finished)
            self.worker_thread.start()

    def on_finished(self, response):
        """Display the response and update the chat log."""
        markdown_content = markdown.markdown(response)
        self.chat_log.append(f"<b>Sutrabot:</b> {markdown_content}")
        self.chat_log.append("")  # New line for readability

        self.loading_label.setVisible(False)
        self.submit_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication([])
    window = SutrabotApp()
    window.show()
    app.exec_()
