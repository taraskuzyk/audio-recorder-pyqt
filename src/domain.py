from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set

import record
from file_system.local_file_system import LocalFileSystem


@dataclass
class Recording:
    text: str
    bytes: bytes = None
    id: str = field(init=False)

    def __post_init__(self):
        self.id = get_text_id(self.text)


def get_text_id(text):
    return "".join([char for char in text if char.isalpha() or char == " "]).lower()


class RecorderManager:
    def __init__(self, path: Path, texts: List[str]):
        self.files = LocalFileSystem(path)
        self.texts = texts
        self.recorder = record.Recorder()
        self.file = None

    def set_device(self, device_index: int):
        self.recorder.input_device_index = device_index

    def start_recording(self, recording: Recording):
        self.file = self.recorder.open("temp.wav")
        self.file.start_recording()

    def stop_recording(self, recording: Recording):
        self.file.stop_recording()
        with open("temp.wav", "rb") as file:
            recording.bytes = file.read()
        self.save_recording(recording)

    def save_recording(self, recording: Recording):
        self.files.add(self.get_file_name(recording), recording.bytes)

    def get_remaining_recordings(self) -> List[Recording]:
        recorded_texts = {
            recording.text for recording in self.get_existing_recordings()
        }
        not_recorded_texts = {*self.texts} - recorded_texts
        return [Recording(text=text) for text in not_recorded_texts]

    def get_existing_recordings(self) -> List[Recording]:
        file_names = self.files.list()
        recorded_ids = {name.replace(".wav", "") for name in file_names}
        return [Recording(text) for text in self.texts if get_text_id(text) in recorded_ids]

    def is_recorded(self, recording: Recording):
        return self.files.get_by_name(self.get_file_name(recording))

    @staticmethod
    def get_file_name(recording: Recording):
        return recording.id + ".wav"
