#!/usr/bin/env python3
"""
Voice-enabled TypeFly Main Controller
This integrates your Ollama + Fast-Whisper setup with TypeFly's drone control system.
Instead of typing commands in the web UI, you can now speak directly to your drone.
Usage:
    python controller/voice_main.py
"""
import sys
import os
import time
from .llm_wrapper import LLMWrapper

try:
    from abs.robot_wrapper import RobotWrapper
except ImportError:
    print("⚠️ TypeFly components not found. Running in standalone mode.")
    DroneWrapper = None

class VoiceTypeFlyCont:
    def __init__(self, use_virtual_robot=True):
        print("🚀 Initializing Voice TypeFly Controller")
        print("=" * 40)

        self.llm = LLMWrapper(temperature=0.1, whisper_model_size="base", enable_audio=True)
        self.use_virtual_robot = use_virtual_robot
        self.drone = None

        if DroneWrapper and not use_virtual_robot:
            try:
                self.drone = DroneWrapper()
                print("🚁 Real drone connected")
            except Exception as e:
                print(f"⚠️ Failed to connect to real drone: {e}")
                print("🔄 Falling back to virtual robot")
                self.use_virtual_robot = True
        else:
            print("🤖 Using virtual robot")

        self.task_history = []

    def process_voice_command(self, language=None):
        if not self.llm.enable_audio:
            return None, "Voice functionality not available", False

        print("\n🎤 Listening for drone command...")
        print("💡 Example commands: 'Find something edible', 'Look for people in the room'")

        try:
            response = self.llm.voice_chat(language=language)
            if response and not response.startswith("Error:"):
                success = self.execute_drone_task(response)
                return "Voice command processed", response, success
            else:
                return None, "Could not process voice input", False
        except Exception as e:
            print(f"❌ Error processing voice command: {e}")
            return None, str(e), False

    def execute_drone_task(self, task_description):
        print(f"🤖 LLM Interpretation: {task_description}")
        self.task_history.append({'timestamp': time.time(), 'task': task_description, 'status': 'processing'})

        if self.use_virtual_robot:
            print("🔄 Virtual robot executing task...")
            time.sleep(2)
            print("✅ Virtual task completed")
            return True
        else:
            print("🚁 Real drone task execution not implemented yet")
            return False

    def interactive_voice_session(self):
        print("\n🎯 Starting Interactive Voice Drone Control")
        print("💡 Commands: Press Enter to record voice command, 'history', 'status', 'quit'")

        while True:
            try:
                user_input = input("\n🎤 Press Enter for voice or type command: ").strip().lower()

                if user_input in ['quit', 'exit', 'q']:
                    print("👋 Shutting down Voice TypeFly Controller")
                    break
                elif user_input == 'history':
                    self.show_task_history()
                elif user_input == 'status':
                    self.show_system_status()
                elif user_input == 'help':
                    self.show_help()
                else:
                    transcription, response, success = self.process_voice_command()
                    print(f"✅ Task completed successfully" if success else f"❌ Task failed: {response}")

            except KeyboardInterrupt:
                print("\n👋 Shutting down Voice TypeFly Controller")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    def show_task_history(self):
        print("\n📋 Task History:")
        if not self.task_history:
            print("No tasks executed yet")
        else:
            for i, task in enumerate(self.task_history[-5:], 1):
                timestamp = time.strftime("%H:%M:%S", time.localtime(task['timestamp']))
                print(f"   {i}. [{timestamp}] {task['task'][:50]}...")

    def show_system_status(self):
        print("\n🔍 System Status:")
        print(f"   🤖 LLM: {'✅ Ready' if self.llm else '❌ Not available'}")
        print(f"   🎤 Audio: {'✅ Ready' if self.llm.enable_audio else '❌ Not available'}")
        print(f"   🚁 Drone: {'🤖 Virtual' if self.use_virtual_robot else '✅ Real' if self.drone else '❌ Disconnected'}")
        print(f"   📋 Tasks completed: {len(self.task_history)}")

    def show_help(self):
        print("\n💡 Voice TypeFly Help:")
        print("   🎤 Voice Commands: 'Find [object]', 'Look around', 'Count [objects]', 'Move [direction]', 'What can you see?'")
        print("   ⌨️ Text Commands: 'history', 'status', 'quit'")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Voice-Controlled TypeFly Drone Controller")
    parser.add_argument("--use_virtual_robot", action="store_true", default=True, help="Use virtual robot instead of real drone")
    parser.add_argument("--whisper_model", default="base", choices=["tiny", "base", "small", "medium", "large-v2"], help="Whisper model size")
    args = parser.parse_args()

    controller = VoiceTypeFlyCont(use_virtual_robot=args.use_virtual_robot)
    if not controller.llm.enable_audio:
        print("❌ Audio not available. Please install: pip install faster-whisper pyaudio")
        return

    controller.interactive_voice_session()

if __name__ == "__main__":
    main()
