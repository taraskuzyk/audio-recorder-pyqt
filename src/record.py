# -*- coding: utf-8 -*-
"""recorder.py
Provides WAV recording functionality via two approaches:
Blocking mode (record for a set duration):
>>> rec = Recorder(channels=2)
>>> with rec.open('blocking.wav', 'wb') as recfile:
...     recfile.record(duration=5.0)
Non-blocking mode (start and stop recording):
>>> rec = Recorder(channels=2)
>>> with rec.open('nonblocking.wav', 'wb') as recfile2:
...     recfile2.start_recording()
...     time.sleep(5.0)
...     recfile2.stop_recording()
"""
from dataclasses import dataclass

import pyaudio
import wave


class Recorder(object):
    """A recorder class for recording audio to a WAV file.
    """

    def __init__(self, channels=2, rate=44100, frames_per_buffer=1024, input_device_index=0):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.input_device_index = input_device_index

    def open(self, fname, mode="wb"):
        return RecordingFile(
            fname, mode, self.channels, self.rate, self.frames_per_buffer, self.input_device_index
        )


@dataclass
class Device:
    index: int
    name: str


def get_devices():
    pa = pyaudio.PyAudio()
    number_of_devices = pa.get_device_count()
    device_dicts = [
        pa.get_device_info_by_index(index)
        for index in range(number_of_devices)
    ]

    return [
        Device(index=device_dict["index"], name=device_dict["name"])
        for device_dict in device_dicts
        if device_dict["hostApi"] == 0 and device_dict["maxInputChannels"] > 0
    ]


class RecordingFile:
    def __init__(self, fname, mode, channels, rate, frames_per_buffer, input_device_index):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None
        self.input_device_index = input_device_index

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            stream_callback=self.get_callback(),
            input_device_index=self.input_device_index
        )
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue

        return callback

    def _prepare_file(self, fname, mode="wb"):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile