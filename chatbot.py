import sys
import subprocess
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QScrollArea
import html  # for escaping HTML characters

class ChatWorker(QThread):
    response_received = pyqtSignal(str, str, str)
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            ollama_command = [
                "ollama", "run", "sudo-self/coder:latest", self.prompt
            ]
            result = subprocess.run(ollama_command, capture_output=True, text=True, check=True)
            self.response_received.emit("Llama", result.stdout.strip(), "color: #32cd32;")
        except subprocess.CalledProcessError as e:
            error_message = f"Error: {e.stderr.strip() if e.stderr else 'Could not get a response from Ollama.'}"
            self.response_received.emit("Llama", error_message, "color: #ff4500;")

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Sudo Llama")
        self.setGeometry(100, 100, 500, 600)

        # Set up layout
        self.layout = QVBoxLayout()

        # Set up chat display area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        # Update stylesheet to ensure text wraps within bounds and add padding
        self.chat_area.setStyleSheet("""
            background-color: #2b2b2b;
            color: white;
            font-size: 14px;
            padding: 10px;
            border: none;
            white-space: pre-wrap;   /* Ensures long text wraps */
            word-wrap: break-word;   /* Breaks long words to fit */
        """)

        # Set up scroll area for the chat window
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.chat_area)

        # Set up message input field
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.setStyleSheet("""
            background-color: #3c3f41;
            color: white;
            font-size: 14px;
            padding: 10px;
            border: none;
        """)
        self.message_input.setFixedHeight(60)

        # Set up send button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            background-color: #1e90ff;
            color: white;
            font-size: 16px;
            padding: 10px;
            border: none;
        """)
        self.send_button.clicked.connect(self.send_message)

        # Add elements to layout
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.message_input)
        self.layout.addWidget(self.send_button)

        # Set the layout of the window
        self.setLayout(self.layout)

    def send_message(self):
        user_message = self.message_input.toPlainText().strip()

        if user_message:
            # Display the user's message in the chat window
            self.display_message("Human", user_message, "color: #1e90ff;")

            # Clear the input field after sending the message
            self.message_input.clear()

            # Start background thread to communicate with Ollama
            self.worker = ChatWorker(user_message)
            self.worker.response_received.connect(self.display_message)
            self.worker.start()

    def display_message(self, sender, message, color_style=""):
        # Escape HTML characters so that they show as raw text
        escaped_message = html.escape(message)

        # Check if the message is code (you can define this based on certain conditions)
        if sender == "Llama" and message.startswith("```"):
            # If it's a code message, format it with <pre> and <code> tags
            formatted_message = f'<p style="{color_style}"><b>{sender}:</b></p><pre style="color: #f8f8f2; background-color: #282c34; padding: 10px; border-radius: 5px;"><code>{escaped_message}</code></pre>'
        else:
            # Regular message format
            formatted_message = f'<p style="{color_style}"><b>{sender}:</b> {escaped_message}</p>'
        
        # Append the formatted message to the chat area as plain text
        self.chat_area.append(formatted_message)

def main():
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
