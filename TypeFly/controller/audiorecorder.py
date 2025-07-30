import pyaudio
import wave
import threading
import time
import os

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        self.audio = pyaudio.PyAudio()
        self.recording = False
        self.frames = []
    
    def start_recording(self):
        """Start recording audio"""
        self.recording = True
        self.frames = []
        
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("🎤 Recording... Press Enter to stop")
            
            while self.recording:
                data = stream.read(self.chunk_size)
                self.frames.append(data)
            
            stream.stop_stream()
            stream.close()
            print("⏹️  Recording stopped")
            
        except Exception as e:
            print(f"Error during recording: {e}")
            self.recording = False
    
    def stop_recording(self):
        """Stop recording"""
        self.recording = False
    
    def save_recording(self, filename="temp_recording.wav"):
        """Save recorded audio to file"""
        try:
            # Save to controller directory by default
            if not os.path.isabs(filename):
                controller_dir = os.path.dirname(__file__)
                filename = os.path.join(controller_dir, filename)
                
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print(f"💾 Audio saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving audio: {e}")
            return None
    
    def record_and_save(self, duration=None, filename=None):
        """Record for specified duration or until stopped"""
        if filename is None:
            filename = f"temp_recording_{int(time.time())}.wav"
            
        recording_thread = threading.Thread(target=self.start_recording)
        recording_thread.start()
        
        if duration:
            time.sleep(duration)
            self.stop_recording()
        else:
            input()  # Wait for Enter key
            self.stop_recording()
        
        recording_thread.join()
        return self.save_recording(filename)
    
    def __del__(self):
        """Cleanup PyAudio"""
        if hasattr(self, 'audio'):
            self.audio.terminate()