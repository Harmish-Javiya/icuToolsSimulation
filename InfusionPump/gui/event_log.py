from PyQt6.QtWidgets import QListWidget


class EventLog(QListWidget):

    def add_log(self, text):

        self.addItem(text)

        self.scrollToBottom()