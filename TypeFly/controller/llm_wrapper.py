import os
import ollama
from faster_whisper import WhisperModel

try:
    from .audiorecorder import AudioRecorder
except ImportError:
    from audiorecorder import AudioRecorder

LLAMA3 = "llama3.2"

class LLMWrapper:
    def __init__(self, temperature=0.0, whisper_model_size="base", enable_audio=True):
        self.temperature = temperature
        self.enable_audio = enable_audio
        self.whisper_model = None
        self.audio_recorder = None

        if self.enable_audio:
            self._initialize_audio(whisper_model_size)

    def _initialize_audio(self, whisper_model_size):
        try:
            print("🔄 Loading Whisper model...")
            self.whisper_model = WhisperModel(whisper_model_size, device="cpu", compute_type="int8")
            self.audio_recorder = AudioRecorder()
            print(f"Whisper model '{whisper_model_size}' loaded successfully")
            print("Audio recording enabled")
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            print("Continuing with text-only mode")
            self.enable_audio = False

    def transcribe_audio(self, audio_file_path, language=None):
        if not self.enable_audio or self.whisper_model is None:
            return "Error: Audio functionality not available"

        try:
            print("Processing recorded audio...")
            segments, info = self.whisper_model.transcribe(audio_file_path, language=language, beam_size=5, word_timestamps=True)
            full_transcription = " ".join(segment.text for segment in segments)
            print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")
            return full_transcription.strip()
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return None

    def voice_chat(self, duration=None, model_name=LLAMA3, stream=False, language=None):
        if not self.enable_audio or self.audio_recorder is None:
            return "Error: Audio functionality not available"

        print("🎙️ Starting voice chat...")
        audio_file = self.audio_recorder.record_and_save(duration)

        if audio_file is None:
            return "Error: Could not record audio"

        try:
            transcribed_text = self.transcribe_audio(audio_file, language)
            if transcribed_text is None or transcribed_text.startswith("Error:"):
                return "Error: Could not transcribe audio"

            print(f"You said: {transcribed_text}")
            response = self.request(transcribed_text, model_name, stream)

            if os.path.exists(audio_file):
                os.remove(audio_file)
                print("Cleaned up temp audio file")

            return response
        except Exception as e:
            print(f"❌ Error in voice chat: {e}")
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
            return None

    def request(self, prompt, model_name=LLAMA3, stream=False):
        messages = [{"role": "user", "content": prompt}]
        if stream:
            return ollama.chat(model=model_name, messages=messages, stream=True)

        resp = ollama.chat(model=model_name, messages=messages)
        return resp["message"]["content"]

if __name__ == "__main__":
    wrapper = LLMWrapper()
    print("🧪 Testing TypeFly LLM Wrapper with Audio Support")
    print("=" * 50)

    print("💬 Testing text chat:")
    response = wrapper.request("Explain photosynthesis in one sentence")
    print(f"🤖 Text Response: {response}")

    print("\n📡 Testing streaming:")
    stream = wrapper.request("Count from 1 to 5", stream=True)
    print("🤖 Streaming Response: ", end="")
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)

    if wrapper.enable_audio:
        print("\n\n🎤 Audio functionality available!")
        print("Run the voice demo with: python examples/voice_chat_demo.py")
    else:
        print("\n\n⚠️ Audio functionality not available")
        print("Install with: pip install faster-whisper pyaudio")
