Content:
Drone control system 
Voice command and chatbox WebUI interface
WebUI with real-time video streaming from drone
Custom YOLO HomeObjects-3k

(Terminal 1) to start server:
cd /home/evas/TypeFly
source .venv/bin/activate  # Optional
python serving/yolo/yolo_service.py
(Terminal 2) to fly:
cd /home/evas/TypeFly
/home/evas/TypeFly/.venv/bin/python serving/webui/typefly_with_voice.py


To connect to drone: 
1. Tello powered on
2. Connect computer to Tello Wifi
3. Drone connects upon starting TypeFly


Note:
Manual takeoff (llm_controller.py)
Web interfance at https://localhost:50001 / Running on local URL:  http://0.0.0.0:50001

