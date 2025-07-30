from llm_wrapper import LLMWrapper

class TypeFlyController:
    def __init__(self):
        # Initialize with voice support
        self.llm = LLMWrapper(enable_audio=True, whisper_model_size="base")
        
    def process_voice_command(self):
        """Process voice command for drone control"""
        print("Speak your drone command...")
        command = self.llm.voice_chat()
        
        if command and not command.startswith("Error:"):
            print(f"Processing: {command}")
            return self.execute_drone_task(command)
        return None
    
    def execute_drone_task(self, task_description):
        """Execute the drone task based on LLM output"""
        # This integrates with TypeFly's existing drone control
        # Original TypeFly logic for task planning goes here
        pass