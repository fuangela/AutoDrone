.PHONY: stop start remove open build typefly-original typefly-voice install-voice check-ollama voice-only test-voice demo-voice clean-audio help-voice setup-dev

SERVICE_LIST = router yolo
SERVICE ?= yolo
GPU_OPTIONS = --gpus all
USE_VIRTUAL_ROBOT ?= true
WHISPER_MODEL ?= base

validate_service:
ifeq ($(filter $(SERVICE),$(SERVICE_LIST)),)
	$(error Invalid SERVICE: [$(SERVICE)], valid values are [$(SERVICE_LIST)])
endif

install_requirements:
	bash ./serving/webui/install_requirements.sh
	cd ./proto && bash generate.sh

# Original Docker targets
stop: validate_service
	@echo "Stopping typefly-$(SERVICE)..."
	@-docker stop -t 0 typefly-$(SERVICE) > /dev/null 2>&1
	@-docker rm -f typefly-$(SERVICE) > /dev/null 2>&1

build: validate_service
	@echo "Building typefly-$(SERVICE)..."
	$(MAKE) stop SERVICE=$(SERVICE)
	$(MAKE) remove SERVICE=$(SERVICE)
	docker build -t typefly-$(SERVICE):0.1 -f docker/$(SERVICE)/Dockerfile .

start: validate_service build
	@echo "Starting typefly-$(SERVICE)..."
	docker run -td --privileged --net=host $(GPU_OPTIONS) --ipc=host \
		--env-file ./docker/env.list \
		--name="typefly-$(SERVICE)" typefly-$(SERVICE):0.1

remove: validate_service
	@echo "Removing typefly-$(SERVICE)..."
	@-docker image rm -f typefly-$(SERVICE):0.1 > /dev/null 2>&1
	@-docker rm -f typefly-$(SERVICE) > /dev/null 2>&1

open: validate_service
	@echo "Entering container shell..."
	docker exec -it typefly-$(SERVICE) bash

# Original TypeFly UI (no voice)
typefly-original:
	@echo "Running original TypeFly UI..."
	$(MAKE) install_requirements
	python3 ./serving/webui/typefly_original.py --use_virtual_robot

# Install voice dependencies
install-voice:
	@echo "Installing audio dependencies..."
	pip install faster-whisper pyaudio ollama

# Check if Ollama is running
check-ollama:
	@echo "Verifying Ollama daemon..."
	@if ! curl -s http://localhost:11434/api/version > /dev/null; then \
		echo "❌ Ollama is not running. Start with: ollama serve"; \
		echo "💡 Then pull a model: ollama pull llama3.2"; \
		exit 1; \
	else \
		echo "✅ Ollama detected"; \
	fi

# Run TypeFly with integrated voice support
typefly-voice: install-voice check-ollama install_requirements
	@echo "Starting TypeFly with integrated voice support..."
	@echo "🚀 Launching TypeFly with Voice UI..."
	python3 ./serving/webui/typefly_with_voice.py \
		$(if $(filter false,$(USE_VIRTUAL_ROBOT)),--no-use_virtual_robot,--use_virtual_robot) \
		--enable_voice \
		--whisper_model $(WHISPER_MODEL)

# Voice-only command line mode (standalone)
voice-only: install-voice check-ollama
	@echo "Starting CLI voice-only mode..."
	python controller/voice_main.py \
		$(if $(filter false,$(USE_VIRTUAL_ROBOT)),--no-use_virtual_robot,--use_virtual_robot) \
		--whisper_model $(WHISPER_MODEL)

# Test voice transcription
test-voice: install-voice
	@echo "Testing voice transcription..."
	python controller/llm_wrapper.py

# Run voice demo
demo-voice: install-voice
	@echo "Running voice demo..."
	@if [ -f examples/voice_chat_demo.py ]; then \
		python examples/voice_chat_demo.py; \
	else \
		echo "❌ Voice demo not found. Creating simple test..."; \
		python -c "from controller.llm_wrapper import LLMWrapper; w = LLMWrapper(); print('Voice test:', w.voice_chat() if w.enable_audio else 'Audio not available')"; \
	fi

# Clean temporary audio files
clean-audio:
	@echo "Cleaning audio temp files..."
	find . -name "temp_recording_*.wav" -delete
	find . -name "*.wav" -path "*/cache/*" -delete

# Help for voice commands
help-voice:
	@echo ""
	@echo "🎤 TypeFly Voice Commands:"
	@echo "========================="
	@echo ""
	@echo "Main Commands:"
	@echo "  make typefly-voice    - Run TypeFly with integrated voice UI"
	@echo "  make typefly-original - Run original TypeFly UI (no voice)"
	@echo "  make voice-only       - Run standalone voice command mode"
	@echo ""
	@echo "Testing & Development:"
	@echo "  make test-voice       - Test voice transcription"
	@echo "  make demo-voice       - Run voice demo"
	@echo "  make install-voice    - Install voice dependencies"
	@echo "  make check-ollama     - Verify Ollama is running"
	@echo "  make clean-audio      - Clean temporary audio files"
	@echo ""
	@echo "Configuration Options:"
	@echo "  USE_VIRTUAL_ROBOT=false  - Use real drone (default: true)"
	@echo "  WHISPER_MODEL=small      - Whisper model size (default: base)"
	@echo ""
	@echo "Examples:"
	@echo "  make typefly-voice USE_VIRTUAL_ROBOT=true WHISPER_MODEL=small"
	@echo "  make voice-only USE_VIRTUAL_ROBOT=false"
	@echo ""
	@echo "Prerequisites:" c
	@echo "  1. Start Ollama: ollama serve"
	@echo "  2. Pull model: ollama pull llama3.2"
	@echo "  3. Install deps: make install-voice"

# Development setup
setup-dev: install-voice install_requirements
	@echo "Setting up development environment..."
	@echo "✅ Development environment ready"
	@echo "💡 Run 'make help-voice' for usage instructions"
