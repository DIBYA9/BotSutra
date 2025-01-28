import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
import markdown

# Load environment variables from the .env file
load_dotenv()

# Fetch the API key from the environment variable
api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is available
if not api_key:
    print("API key is missing. Please set it in the .env file.")
    exit()

# Configure the API
genai.configure(api_key=api_key)

# Create the model
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

# Full prompt for Sutrabot
full_prompt = """
You are Sutrabot, a wise, pragmatic mentor offering practical advice. You provide clear, actionable, step-by-step solutions to life’s challenges. While grounded in modern problem-solving, you occasionally draw upon wisdom from the Vedas, Bhagavad Gita, and Chanakya Niti to provide deeper insights. Your tone is approachable, concise, and focused on empowering the user.
input: Who are you?
output: I am your guide Sutrabot, here to help you navigate life’s complexities with wisdom from ancient teachings, blending timeless principles with practical advice to illuminate your path.
input: Why are you here?
output: My purpose is to help you find clarity, balance, and success by offering guidance rooted in both ancient wisdom and modern practicality. I’m here to help you grow and overcome life’s obstacles.
input: Where are you?
output: I exist wherever wisdom is sought. While my knowledge is vast, I am always within reach whenever you seek insight or guidance.
input: What is the meaning of life?
output: Life’s meaning lies in self-realization, as taught in the Upanishads. It is a journey to transcend attachments and align with one’s higher purpose, seeking knowledge, fulfilling dharma, and understanding the oneness of the self with the universe.
input: Can you help me with my problems?
output: Yes, I can. Like Chanakya said, every problem has a solution when approached with strategy and patience. Share your concerns, and I’ll guide you with clear, practical steps rooted in wisdom.
"""

def generate(input_text):
    # Combine the full prompt with the user input
    prompt_with_input = f"{full_prompt}\ninput: {input_text}\noutput: "
    
    # Generate content based on the combined prompt
    response = model.generate_content([prompt_with_input])
    return response.text

# Worker thread to simulate Jarvis-like loading
class WorkerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, input_text):
        super().__init__()
        self.input_text = input_text

    def run(self):
        # Simulate a delay for loading
        response = generate(self.input_text)
        self.finished.emit(response)


class SutrabotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sutrabot: Your Wise Guide")
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet("""
            background-color: #1A1A1A;
            color: white;
            font-family: Arial, sans-serif;
            border-radius: 15px;  /* Round corners for the main window */
            padding: 10px;
        """)
        
        # Create layout
        layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel("Sutrabot: Your Wise Guide")
        self.title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #4CAF50; 
            padding: 10px;
            text-align: center;
            border-radius: 10px;
        """)
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        # Input field for questions
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Ask a question...")
        self.input_field.setStyleSheet("""
            font-size: 16px;
            padding: 10px;
            background-color: #333;
            color: white;
            border-radius: 10px;  /* Rounded corners for the input field */
        """)
        layout.addWidget(self.input_field)

        # Ask button with hover and click effect
        self.submit_button = QPushButton("Ask", self)
        self.submit_button.setStyleSheet("""
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            border-radius: 10px;  /* Rounded corners for the button */
            transition: background-color 0.3s ease;
        """)
        self.submit_button.setFixedSize(120, 40)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setStyleSheet("""
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            border-radius: 10px;
        """)
        layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

        # Output area with markdown rendering
        self.output_area = QTextEdit(self)
        self.output_area.setStyleSheet("""
            font-size: 14px; 
            background-color: #222;
            color: white;
            padding: 10px;
            border-radius: 10px;  /* Rounded corners for the output area */
        """)
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Progress label for loading
        self.loading_label = QLabel("BY DIBYADIP MITRA")
        self.loading_label.setStyleSheet("""
            font-size: 18px;
            color: #FF9800;
            padding: 10px;
            display: none;
            border-radius: 10px;
        """)
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def on_submit(self):
        user_input = self.input_field.text().strip()
        if user_input:
            self.loading_label.setStyleSheet("display: block; font-size: 18px; color: #FF9800; padding: 10px; border-radius: 10px;")
            self.loading_label.show()
            self.submit_button.setEnabled(False)
            self.worker_thread = WorkerThread(user_input)
            self.worker_thread.finished.connect(self.on_finished)
            self.worker_thread.start()

    def on_finished(self, response):
        # Process and render markdown content
        markdown_content = markdown.markdown(response)
        self.output_area.setHtml(markdown_content)

        # Hide loading and re-enable submit button
        self.loading_label.hide()
        self.submit_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication([])
    window = SutrabotApp()
    window.show()
    app.exec_()
