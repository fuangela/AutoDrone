# AutoDrone 
This repo is taken from https://github.com/typefly/TypeFly. In Autodrone,I changed the LLM used for robot task planning from GPT-4 to llama3.2, I have added fastwhisper and trained the Yolo model on HomeObjects-3k dataset https://docs.ultralytics.com/datasets/detect/homeobjects-3k/#dataset-yaml

## Content
Drone control system 
Voice command and chatbox WebUI interface
WebUI with real-time video streaming from drone
Custom YOLO HomeObjects-3k

## To run
(Terminal 1) to start server:
```bash 
cd /home/evas/TypeFly
source .venv/bin/activate  # Optional
python serving/yolo/yolo_service.py
```
(Terminal 2) to fly:
```bashcd /home/evas/TypeFly
/home/evas/TypeFly/.venv/bin/python serving/webui/typefly_with_voice.py
```
## Tello Drone
To connect to drone: 
1. Tello powered on
2. Connect computer to Tello Wifi
3. Drone connects upon starting TypeFly

## Notes
Manual takeoff: uncomment automatic takeoff section in llm_controller.py
Web interfance at https://localhost:50001 / Running on local URL:  http://0.0.0.0:50001
To change to virtual robot: uncomment robot_type = RobotType.VIRTUAL in typefly_with_voice.py
