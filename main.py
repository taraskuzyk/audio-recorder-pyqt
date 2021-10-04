import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pyaudio
import wave
from record import Recorder
import time
import requests
import json

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.keepRecording = True
        self.button_state = 'record'

        uic.loadUi('asr.ui', self)
        self.show()
        self.send_button.clicked.connect(self.on_click)
        self.setWindowTitle("Celloscope ASR")

        self.recorder = Recorder(channels=2, rate=16000, frames_per_buffer=1024)
        
    def clear_texts(self):
        self.processing_time_text.setText("")
        self.similarity_score_text.setText("")


    def on_click(self):
        if self.button_state == 'record':
            self.recFile = self.recorder.open('test.wav', 'wb')
            self.recFile.start_recording()
            self.transcription_text.setText("Say Something in Pure Bangla!!")
            self.send_button.setText("Send")
            self.button_state = 'send'
            self.clear_texts()
        else:
            self.recFile.stop_recording()
            self.transcription_text.setText("Sending audio to server ... Please wait!!")
            self.text_transcript()
            self.send_button.setText("Record")
            self.button_state = 'record'
            # self.clear_texts()
         

    def text_transcript(self):
        request_json = {
            'files': open('test.wav', 'rb')
        }
        
        response = requests.post(
            "https://nlp.celloscope.net/nlp/dataset/v1/audio/speech-to-text", 
            data={'referenceText' : self.reference_text_edit.toPlainText()},
            files=request_json
        )

        json_response = json.loads(response.text)
        transcript = json_response['text']
        processing_time = json_response['processingTime']
        similarity = json_response['similarity']

        print(json_response)
        print(f"found : {transcript}")

        self.transcription_text.setText(transcript)
        self.processing_time_text.setText(processing_time)
        if similarity == '0%' :
            self.similarity_score_text.setText("")
        else: self.similarity_score_text.setText(f"Similarity with reference text is {similarity}")


def main():
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec_())
	
if __name__ == '__main__':
    main()
