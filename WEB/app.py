import sys
import os
import asyncio
import threading
import traceback
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add parent directory to sys.path so we can import OmniAI modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.audio_stream import WebAudioStream
from runtime.audio_pipeline import AudioPipeline
from runtime.controller import RuntimeController
from config import AUDIO

app = FastAPI(title="OmniAI Web Blackbox")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def get_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.websocket("/ws/omni")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Queue for sending messages from synchronous callbacks to the async websocket
    send_queue = asyncio.Queue()
    
    # Capture the main event loop to use in the background thread callbacks
    loop = asyncio.get_running_loop()
    
    def on_chord_change(prediction):
        # Convert int64 and arrays to standard python types for JSON serialization
        msg = {
            "type": "chord",
            "chord": prediction["chord"],
            "root": prediction["root"],
            "quality": prediction["quality"],
            "notes": [int(n) for n in prediction["notes"]]
        }
        asyncio.run_coroutine_threadsafe(send_queue.put(msg), loop)

    def on_key_locked(key_name):
        msg = {
            "type": "key_locked",
            "key": key_name
        }
        asyncio.run_coroutine_threadsafe(send_queue.put(msg), loop)

    stream = WebAudioStream()
    pipeline = AudioPipeline(custom_stream=stream)
    controller = RuntimeController(
        web_mode=True, 
        on_chord_change=on_chord_change,
        on_key_locked=on_key_locked
    )
    
    pipeline.start()
    
    # Background thread to run the synchronous audio pipeline
    def run_pipeline():
        try:
            for note in pipeline.notes():
                if note is None:
                    continue
                controller.add_note(note)
                controller.update()
        except Exception as e:
            print(f"Pipeline thread error: {e}")
            traceback.print_exc()

    thread = threading.Thread(target=run_pipeline, daemon=True)
    thread.start()

    # Async task to send messages from the queue to the websocket
    async def send_worker():
        try:
            while True:
                msg = await send_queue.get()
                await websocket.send_json(msg)
        except Exception as e:
            print(f"Send worker error: {e}")

    send_task = asyncio.create_task(send_worker())

    try:
        while True:
            # Receive raw float32 PCM bytes from the browser
            data = await websocket.receive_bytes()
            samples = np.frombuffer(data, dtype=np.float32)
            
            # Feed into the pipeline
            stream.put_chunk(samples, AUDIO.SAMPLE_RATE)
            
            # Generate synth output chunk (always perfectly synchronized with input)
            if controller.key_locked:
                out_audio = controller.engine.synth.generate_chunk(len(samples))
            else:
                out_audio = np.zeros(len(samples), dtype=np.float32)
            
            # Send raw float32 PCM back to the browser
            await websocket.send_bytes(out_audio.tobytes())
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        send_task.cancel()
        stream.stop()
        pipeline.stop()
        controller.clear()
