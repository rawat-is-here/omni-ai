"""
OmniAI

Main application entry point.

Listens to the microphone,
detects notes,
predicts accompaniment,
and plays it live.
"""

from __future__ import annotations

import argparse
import traceback

import cv2
import threading

from runtime.audio_pipeline import AudioPipeline
from runtime.controller import RuntimeController


def main():

    parser = argparse.ArgumentParser(description="OmniAI Live Accompanist with Camera")
    parser.add_argument("--key", type=str, help="Lock to a specific key, e.g., 'C Major' or 'A Minor'")
    args = parser.parse_args()

    print("=" * 60)
    print("OmniAI - AR Camera Mode")
    print("=" * 60)
    print()
    print("Opening Camera...")
    
    # State variables for UI overlay
    current_scale = "Detecting Scale... (Sing for 8s)"
    current_chord = "--"
    
    def on_chord_change(prediction):
        nonlocal current_chord
        current_chord = prediction["chord"]
        
    def on_key_locked(key_name):
        nonlocal current_scale
        current_scale = f"Scale Locked: {key_name}"

    pipeline = AudioPipeline()
    controller = RuntimeController(
        fixed_key_str=args.key,
        on_chord_change=on_chord_change,
        on_key_locked=on_key_locked
    )
    
    # Run the audio pipeline in a background daemon thread
    def audio_thread_loop():
        try:
            for note in pipeline.notes():
                if note is None:
                    continue
                controller.add_note(note)
                controller.update()
        except Exception:
            print("Audio thread exception:")
            traceback.print_exc()

    pipeline.start()
    audio_thread = threading.Thread(target=audio_thread_loop, daemon=True)
    audio_thread.start()

    # Open the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        pipeline.stop()
        controller.clear()
        return

    print("Camera opened. Press 'q' on the video window to quit.")
    
    cv2.namedWindow('OmniAI', cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break
                
            # Flip the frame horizontally for a mirror effect
            frame = cv2.flip(frame, 1)
            
            # Overlay Scale Status
            cv2.putText(
                frame, 
                current_scale, 
                (30, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1.0, 
                (0, 255, 0) if "Locked" in current_scale else (0, 165, 255), 
                2, 
                cv2.LINE_AA
            )
            
            # Overlay Current Chord
            cv2.putText(
                frame, 
                f"Chord: {current_chord}", 
                (30, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1.5, 
                (255, 255, 255), 
                3, 
                cv2.LINE_AA
            )
            
            cv2.imshow('OmniAI', frame)
            
            # Check for 'q' key to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nQuitting...")
                break

    except Exception:
        print()
        print("Unexpected error in video loop:")
        traceback.print_exc()

    finally:
        cap.release()
        cv2.destroyAllWindows()
        pipeline.stop()
        controller.clear()
        print("Goodbye.")


if __name__ == "__main__":

    main()