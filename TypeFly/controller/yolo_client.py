from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import json
import os
import queue
import asyncio
import requests
from contextlib import asynccontextmanager

from .utils import print_t
from .shared_frame import SharedFrame, Frame

DIR = os.path.dirname(os.path.abspath(__file__))

VISION_SERVICE_IP = os.environ.get("VISION_SERVICE_IP", "localhost")
ROUTER_SERVICE_PORT = os.environ.get("ROUTER_SERVICE_PORT", "50049")

class YoloClient():
    def __init__(self, shared_frame: Optional[SharedFrame] = None):
        self.service_url = f'http://{VISION_SERVICE_IP}:{ROUTER_SERVICE_PORT}/yolo'
        self.image_size = (640, 352)
        self.frame_queue = queue.Queue()  # queue element: frame only for sync calls
        self.shared_frame = shared_frame
        self.frame_id = 0
        self.frame_id_lock = asyncio.Lock()

    def is_local_service(self):
        return VISION_SERVICE_IP == 'localhost'

    @staticmethod
    def image_to_bytes(image: Image.Image) -> bytes:
        """Convert PIL Image to compressed WEBP bytes."""
        imgByteArr = BytesIO()
        image.save(imgByteArr, format='WEBP')
        return imgByteArr.getvalue()

    @staticmethod
    def plot_results(frame: Image.Image, results):
        """Draw bounding boxes and labels on frame from results dict."""
        if results is None:
            return

        def str_float_to_int(value, multiplier):
            return int(float(value) * multiplier)

        draw = ImageDraw.Draw(frame)
        font_path = os.path.join(DIR, "assets/Roboto-Medium.ttf")
        font = ImageFont.truetype(font_path, size=50)
        w, h = frame.size

        for result in results:
            box = result.get("box", {})
            draw.rectangle(
                (
                    str_float_to_int(box.get("x1", 0), w),
                    str_float_to_int(box.get("y1", 0), h),
                    str_float_to_int(box.get("x2", 0), w),
                    str_float_to_int(box.get("y2", 0), h),
                ),
                fill=None,
                outline='blue',
                width=4,
            )
            draw.text(
                (str_float_to_int(box.get("x1", 0), w), str_float_to_int(box.get("y1", 0), h) - 50),
                result.get("name", ""),
                fill='red',
                font=font,
            )

    @staticmethod
    def plot_results_oi(frame: Image.Image, object_list):
        """Draw bounding boxes and labels for a list of objects (with x,y,w,h attributes)."""
        if not object_list:
            return

        def str_float_to_int(value, multiplier):
            return int(float(value) * multiplier)

        draw = ImageDraw.Draw(frame)
        font_path = os.path.join(DIR, "assets/Roboto-Medium.ttf")
        font = ImageFont.truetype(font_path, size=50)
        w, h = frame.size

        for obj in object_list:
            draw.rectangle(
                (
                    str_float_to_int(obj.x - obj.w / 2, w),
                    str_float_to_int(obj.y - obj.h / 2, h),
                    str_float_to_int(obj.x + obj.w / 2, w),
                    str_float_to_int(obj.y + obj.h / 2, h),
                ),
                fill=None,
                outline='blue',
                width=4,
            )
            draw.text(
                (str_float_to_int(obj.x - obj.w / 2, w), str_float_to_int(obj.y - obj.h / 2, h) - 50),
                obj.name,
                fill='red',
                font=font,
            )

    def retrieve(self) -> Optional[SharedFrame]:
        return self.shared_frame

    def detect_local(self, frame: Frame, conf=0.2):
        """
        Synchronous detection by sending HTTP POST to YOLO server.

        Args:
            frame (Frame): Frame object containing PIL image.
            conf (float): Confidence threshold for detection.
        """
        try:
            image = frame.image
            if image is None:
                print_t("[Y] Warning: frame.image is None")
                return

            resized_image = image.resize(self.image_size)
            image_bytes = self.image_to_bytes(resized_image)
            self.frame_queue.put(frame)

            config = {
                'user_name': 'yolo',
                'stream_mode': True,
                'image_id': self.frame_id,
                'conf': conf,
            }
            files = {
                'image': ('image.webp', image_bytes),
                'json_data': (None, json.dumps(config)),
            }

            print_t(f"[Y] Sending request to {self.service_url}")
            response = requests.post(self.service_url, files=files)
            print_t(f"[Y] Response: {response.text}")

            json_results = json.loads(response.text)
            if self.shared_frame is not None:
                self.shared_frame.set(self.frame_queue.get(), json_results)

            self.frame_id += 1

        except Exception as e:
            print_t(f"[Y] Exception in detect_local: {e}")

    @asynccontextmanager
    async def get_aiohttp_session_response(self, service_url, data, timeout_seconds=3):
        """
        Async context manager for aiohttp POST request with timeout.
        """
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(service_url, data=data) as response:
                    response.raise_for_status()
                    yield response
        except aiohttp.ServerTimeoutError:
            print_t(f"[Y] Timeout error when connecting to {service_url}")
        except Exception as e:
            print_t(f"[Y] Exception in aiohttp request: {e}")

    async def detect(self, frame: Frame, conf=0.3):
        """
        Async detection. Calls sync detect_local if local service.
        Otherwise sends async HTTP request to YOLO server.
        """
        if self.is_local_service():
            self.detect_local(frame, conf)
            return

        image = frame.image
        if image is None:
            print_t("[Y] Warning: frame.image is None in async detect")
            return

        resized_image = image.resize(self.image_size)
        image_bytes = self.image_to_bytes(resized_image)

        async with self.frame_id_lock:
            self.frame_queue.put((self.frame_id, frame))
            config = {
                'user_name': 'yolo',
                'stream_mode': True,
                'image_id': self.frame_id,
                'conf': conf,
            }
            files = {
                'image': image_bytes,
                'json_data': json.dumps(config),
            }
            self.frame_id += 1

        async with self.get_aiohttp_session_response(self.service_url, files) as response:
            if response is None:
                print_t("[Y] No response received from YOLO server.")
                return
            results = await response.text()

        try:
            json_results = json.loads(results)
        except json.JSONDecodeError:
            print_t(f"[Y] Invalid JSON results: {results}")
            return

        # Discard old images
        if self.frame_queue.empty():
            return
        while self.frame_queue.queue[0][0] < json_results.get('image_id', -1):
            self.frame_queue.get()
        # Discard old results
        if self.frame_queue.queue[0][0] > json_results.get('image_id', -1):
            return

        if self.shared_frame is not None:
            self.shared_frame.set(self.frame_queue.get()[1], json_results)
