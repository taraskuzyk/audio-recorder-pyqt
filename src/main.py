import os
import shutil
import sys
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import *

from domain import RecorderManager, Recording
from record import get_devices

"""
Todo:

1) select folder to record to (with ability to create a new one)
2) create prompts one by one in alphabetical order base
optional) select csv to get first names from (or full names) and select the header for the column - then show the top 100 / 150 names and their occurences in % and total % covered

"""
basedir = Path(os.path.dirname(__file__))


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        uic.loadUi(basedir / "asr.ui", self)

        self.recorder_manager = RecorderManager(basedir / "_storage", get_texts())

        self.show()
        self.not_recorded_texts.setVerticalScrollBar(self.not_recorded_texts_scroll_bar)
        self.recorded_texts.setVerticalScrollBar(self.recorded_texts_scroll_bar)
        self.toggle_record.clicked.connect(self.record_toggle)
        self.populate_tables()
        self.initiate_devices()
        self.save_to.clicked.connect(self.save_recordings_to_folder)

    def populate_tables(self):
        self._clear_tables()
        for recording in self.recorder_manager.get_remaining_recordings():
            self.not_recorded_texts.addItem(RecordingItem(recording))
        for recording in self.recorder_manager.get_existing_recordings():
            self.recorded_texts.addItem(RecordingItem(recording))
        self.change_text_to_record()

    def _clear_tables(self):
        self.not_recorded_texts.clear()
        self.recorded_texts.clear()

    def change_text_to_record(self):
        if self.not_recorded_texts.count() > 0:
            text = self.get_current_recording().text
        else:
            text = "No more text to read!"
        self.text_to_read.setText(text)

    def initiate_devices(self):
        devices = get_devices()
        for device in devices:
            self.devices.addItem(device.name)
        self.devices.currentIndexChanged.connect(self.change_device)

    def change_device(self, device_index: int):
        self.recorder_manager.set_device(device_index)

    def record_toggle(self):
        current_recording = self.get_current_recording()
        if self.is_recording():
            self.recorder_manager.stop_recording(current_recording)
            self.populate_tables()
            self.toggle_record.setText("Record")
        else:
            self.recorder_manager.start_recording(current_recording)
            self.toggle_record.setText("Stop")

    def get_current_recording(self):
        return self.recorder_manager.get_remaining_recordings()[0]

    def is_recording(self) -> bool:
        return self.toggle_record.text() == "Stop"

    def save_recordings_to_folder(self):
        directory_path = Path(
            str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        )
        storage_dir = basedir / f"_storage"
        names = os.listdir(storage_dir)
        for name in names:
            shutil.copy(basedir / "_storage" / name, directory_path)


class RecordingItem(QListWidgetItem):
    def __init__(self, recording: Recording):
        super().__init__()
        self.recording = recording
        self.setText(recording.text)


def get_texts():
    with open(basedir / "texts.csv") as file:
        return file.read().split("\n")


def main():
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
