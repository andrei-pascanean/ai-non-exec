from flask import Flask, render_template
import tempfile
import base64
import traceback
import whisper
from flask_sockets import Sockets
from werkzeug.routing import Rule

app = Flask(__name__)
sockets = Sockets(app)

# Load the model at startup
model = whisper.load_model('base.en')

def process_wav_bytes(webm_bytes: bytes, sample_rate: int = 16000):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as temp_file:
        temp_file.write(webm_bytes)
        temp_file.flush()
        waveform = whisper.load_audio(temp_file.name, sr=sample_rate)
        return waveform

def transcribe_socket(ws):
    print("endpoint pinged")
    while not ws.closed:
        message = ws.receive()
        if message:
            print('message received', len(message), type(message))
            try:
                if isinstance(message, str):
                    message = base64.b64decode(message)
                audio = process_wav_bytes(bytes(message))
                audio = whisper.pad_or_trim(audio)
                transcription = model.transcribe(audio)
                # Extract the text from the transcription result and send it back
                text = transcription['text'].strip()
                if text:
                    ws.send(text)
                    print(f"Sent transcription: {text}")
            except Exception as e:
                error_msg = f"Error processing audio: {str(e)}"
                print(error_msg)
                traceback.print_exc()
                ws.send(error_msg)

@app.route('/')
def index():
    return render_template('index.html')

sockets.url_map.add(Rule('/transcribe', endpoint=transcribe_socket, websocket=True))

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', 5003), app, handler_class=WebSocketHandler)
    server.serve_forever()