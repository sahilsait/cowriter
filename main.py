from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
import requests
import chromadb
import json

class CoWriterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def setup_chroma_db(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="writing_samples",
            metadata={'description': "User writing samples and improvements"},
        )

    def init_ui(self):
        # Main window setup
        self.setWindowTitle("AI Co-Writer")
        self.setGeometry(100, 100, 1400, 800)
        
        # Set up the central widget and main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left pane (User Input) setup
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Input area label
        input_label = QLabel("Your Text")
        input_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        left_layout.addWidget(input_label)
        
        # Text input area
        self.user_text = QTextEdit()
        self.user_text.setPlaceholderText("Start writing here...")
        self.user_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        left_layout.addWidget(self.user_text)
        
        # Submit button
        submit_btn = QPushButton("Get AI Suggestions")
        submit_btn.clicked.connect(self.process_text)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        submit_btn_container = QHBoxLayout()
        submit_btn_container.addStretch()
        submit_btn_container.addWidget(submit_btn)
        submit_btn_container.addStretch()
        left_layout.addLayout(submit_btn_container)
        
        # Right pane (AI Output) setup
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Output area label
        output_label = QLabel("AI Suggestions")
        output_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        right_layout.addWidget(output_label)
        
        # AI output area
        self.ai_text = QTextEdit()
        self.ai_text.setReadOnly(True)
        self.ai_text.setPlaceholderText("AI suggestions will appear here...")
        self.ai_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        right_layout.addWidget(self.ai_text)
        
        # Feedback buttons
        feedback_layout = QHBoxLayout()
        accept_btn = QPushButton("Accept Changes")
        reject_btn = QPushButton("Reject Changes")
        for btn in [accept_btn, reject_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 13px;
                }
            """)
        accept_btn.setStyleSheet(accept_btn.styleSheet() + """
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        reject_btn.setStyleSheet(reject_btn.styleSheet() + """
            QPushButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        feedback_layout.addStretch()
        feedback_layout.addWidget(accept_btn)
        feedback_layout.addWidget(reject_btn)
        feedback_layout.addStretch()
        right_layout.addLayout(feedback_layout)
        
        # Add both panes to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial splitter sizes (50-50 split)
        splitter.setSizes([700, 700])
        
        # Add splitter to main layout
        layout.addWidget(splitter)
        
        # Add status bar
        self.statusBar().showMessage("Ready")
        
        # Add menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        new_action = file_menu.addAction("New")
        new_action.setShortcut("Ctrl+N")
        save_action = file_menu.addAction("Save")
        save_action.setShortcut("Ctrl+S")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        undo_action = edit_menu.addAction("Undo")
        undo_action.setShortcut("Ctrl+Z")
        redo_action = edit_menu.addAction("Redo")
        redo_action.setShortcut("Ctrl+Y")
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        style_action = settings_menu.addAction("Writing Style Preferences")

    def process_text(self):
        # Get text from user input
        user_text = self.user_text.toPlainText()
        
        if not user_text.strip():
            QMessageBox.warning(self, "Warning", "Please enter some text first!")
            return
            
        self.statusBar().showMessage("Processing...")
        
        try:
            # Call Ollama API
            response = requests.post('http://localhost:11434/api/chat',
                json={
                    "model": "llama3.2:3b",
                    "messages": [
                        {"role": "system", "content": "You are a helpful writing assistant. Improve the following text while maintaining the author's style. Give only the improved text."},
                        {"role": "user", "content": user_text}
                    ],
                    "stream": False,
                })

            if response.status_code == 200:
                result = response.json()
                # Extract just the content from the nested message
                print(result['message']['content'])
                self.ai_text.setText(result['message']['content'])
                self.statusBar().showMessage("Ready")
                
            else:
                self.statusBar().showMessage(f"Error: API returned status {response.status_code}")
                QMessageBox.critical(self, "Error", f"API error: {response.status_code}")

        except Exception as e:
            self.statusBar().showMessage("Error processing text")
            QMessageBox.critical(self, "Error", f"Failed to process text: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = CoWriterApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()