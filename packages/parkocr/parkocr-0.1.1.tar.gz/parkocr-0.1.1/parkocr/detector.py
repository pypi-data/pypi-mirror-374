import os
import re
import cv2
import time
import logging
import easyocr
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from ultralytics.engine.results import Results


os.environ["YOLO_VERBOSE"] = "False"
Results.print = lambda self: None
logging.getLogger("ultralytics").setLevel(logging.WARNING)

_PLATE_RE = re.compile(r"^[A-Z]{3}[0-9][0-9A-Z][0-9]{2}$")
YOLO_MODEL = [
    "yolov8n.pt",
    "yolov8s.pt",
    "yolov8m.pt",
    "yolov8l.pt",
    "yolov8x.pt"
]


class Detector:
    """
    License plate reader using YOLO to locate regions and EasyOCR to read the text.

    Features:
        - Filters by ROI (quadrant) defined with frame coordinates (x1, y1, x2, y2)
        - `headless=True`: runs without creating a window or drawing overlays
        - Prevents freezing on the same consecutively repeated plate
        - Optional FIFO output for inter-process communication
        - Optional screenshot saving ("full" = whole frame, "roi" = only ROI, None = disabled)

    Args:
        rtsp_url (str): The RTSP URL or video source (e.g., RTSP stream, file path, webcam index).
        model_size (int, optional): Index of YOLO model size to use, based on YOLO_MODEL list.
        conf_thresh (float, optional): Minimum YOLO detection confidence threshold.
        roi (tuple[int, int, int, int] | None, optional): Region of interest as (x1, y1, x2, y2).
        headless (bool, optional): If True, disables window display and overlays.
        window_size (tuple[int, int], optional): Display window size (width, height).
        process_interval_s (float, optional): Seconds between detection cycles.
        freeze_seconds (float, optional): Seconds to freeze display after detection.
        ocr_langs (list[str], optional): Languages to use for EasyOCR.
        on_detect (callable, optional): Callback invoked with the detected plate.
        min_ocr_conf (float, optional): Minimum OCR confidence required to accept text.
        fifo_output (str | None, optional): Path to FIFO file. If set, detected plates will be written there.
        screenshot (str | None, optional): Screenshot mode.
            None = disabled,
            "full" = save whole frame,
            "roi" = save only the ROI region.
    """

    def __init__(
        self,
        rtsp_url: str,
        model_size: int = 0,
        conf_thresh: float = 0.5,
        roi: tuple[int, int, int, int] | None = None,
        headless: bool = False,
        window_size: tuple[int, int] = (1280, 720),
        process_interval_s: float = 1.0,
        freeze_seconds: float = 0.5,
        ocr_langs: list[str] = ["en"],
        on_detect=None,
        min_ocr_conf: float = 0.30,
        fifo_output: str | None = None,
        screenshot: str | None = None
    ):
        self.rtsp_url = rtsp_url
        self.conf_thresh = conf_thresh
        self.roi = roi
        self.headless = headless
        self.window_width, self.window_height = window_size
        self.process_interval_s = process_interval_s
        self.freeze_seconds = freeze_seconds
        self.on_detect = on_detect
        self.min_ocr_conf = min_ocr_conf
        self.fifo_output = fifo_output
        self.screenshot = screenshot
        if self.screenshot not in (None, "full", "roi"):
            raise ValueError("screenshot must be None, 'full', or 'roi'")
        if self.screenshot is not None:
            os.makedirs("plates", exist_ok=True)
        if self.fifo_output and not os.path.exists(self.fifo_output):
            os.mkfifo(self.fifo_output)
        self._yolo = YOLO(YOLO_MODEL[model_size], verbose=False)
        self._ocr = easyocr.Reader(ocr_langs, verbose=False)
        self._last_process_time = 0.0
        self._last_plate = None

    def _open_fifo(self):
        if not self.fifo_output:
            return None
        if not os.path.exists(self.fifo_output):
            os.mkfifo(self.fifo_output)
        try:
            return os.open(self.fifo_output, os.O_WRONLY | os.O_NONBLOCK)
        except OSError:
            return None

    def _write_fifo(self, fd, plate: str):
        if fd is None:
            return
        try:
            os.write(fd, (plate + "\n").encode())
        except OSError:
            pass

    def _save_screenshot(self, frame):
        if self.screenshot is None:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join("plates", f"{self._last_plate}_{timestamp}.jpg")
        if self.screenshot == "full":
            img_to_save = frame
        elif self.screenshot == "roi":
            x1, y1, x2, y2 = self.roi
            img_to_save = frame[y1:y2, x1:x2]
        else:
            return
        cv2.imwrite(filename, img_to_save)
        logging.info(f"Screenshot saved: {filename}")

    def run(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        if not cap.isOpened():
            raise RuntimeError(f"Cant open stream on: {self.rtsp_url}")
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError("Error reading initial frame")
        logging.info(f"Video stream started: {self.rtsp_url} | headless={self.headless}")
        fifo_fd = self._open_fifo()
        if self.roi is None:
            self.roi = self._default_center_square_roi(frame)
        if not self.headless:
            cv2.namedWindow("LPR", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("LPR", self.window_width, self.window_height)
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.03)
                    continue
                now = time.time()
                if (now - self._last_process_time) >= self.process_interval_s:
                    self._last_process_time = now
                    det = self._detect_and_read(frame, self.roi)
                    if det is not None:
                        plate_text, bbox = det
                        if plate_text != self._last_plate:
                            self._last_plate = plate_text
                            if callable(self.on_detect):
                                try:
                                    self.on_detect(plate_text)
                                except Exception:
                                    logging.exception("on_detect callback error")
                            else:
                                logging.info(f"Plate: {plate_text}")
                            self._write_fifo(fifo_fd, plate_text)
                            self._save_screenshot(frame)
                            if not self.headless:
                                self._draw_polygon(frame, bbox, color=(0, 0, 255), thickness=2)
                                self._draw_ruler_and_roi(frame, self.roi)
                                px, py = bbox[0]
                                cv2.putText(frame, plate_text, (px, py - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                                end = time.time() + self.freeze_seconds
                                while time.time() < end:
                                    disp = cv2.resize(frame, (self.window_width, self.window_height))
                                    cv2.imshow("LPR", disp)
                                    if cv2.waitKey(1) & 0xFF == ord('q'):
                                        cap.release()
                                        cv2.destroyAllWindows()
                                        return
                                    time.sleep(0.01)
                if not self.headless:
                    self._draw_ruler_and_roi(frame, self.roi)
                    disp = cv2.resize(frame, (self.window_width, self.window_height))
                    cv2.imshow("LPR", disp)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nShutting down…")
        finally:
            cap.release()
            if fifo_fd:
                os.close(fifo_fd)
            if not self.headless:
                cv2.destroyAllWindows()

    def _detect_and_read(self, frame, roi):
        results = self._yolo(frame)
        r = results[0]
        for *box, conf, _cls in r.boxes.data.cpu().numpy():
            if conf < self.conf_thresh:
                continue
            x1, y1, x2, y2 = map(int, box)
            region = frame[y1:y2, x1:x2]
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            ocr_results = self._ocr.readtext(gray, detail=1)
            for bbox, text, conf_ocr in ocr_results:
                if conf_ocr < self.min_ocr_conf:
                    continue
                original_text = (text or "").strip().upper()
                clean = re.sub(r"[^A-Z0-9]", "", original_text)
                if _PLATE_RE.match(clean):
                    bbox_global = [(int(pt[0] + x1), int(pt[1] + y1)) for pt in bbox]
                    cx = sum(p[0] for p in bbox_global) // 4
                    cy = sum(p[1] for p in bbox_global) // 4
                    rx1, ry1, rx2, ry2 = roi
                    if (rx1 <= cx <= rx2) and (ry1 <= cy <= ry2):
                        return (clean, bbox_global) 
        return None

    @staticmethod
    def _default_center_square_roi(frame, frac: float = 0.2, aspect_ratio: float = 3.07):
        h, w = frame.shape[:2]
        roi_w = int(w * frac)
        roi_h = int(roi_w / aspect_ratio)
        cx, cy = w // 2, h // 2
        x1 = max(0, cx - roi_w // 2)
        y1 = max(0, cy - roi_h // 2)
        x2 = min(w - 1, x1 + roi_w)
        y2 = min(h - 1, y1 + roi_h)
        return (x1, y1, x2, y2)

    @staticmethod
    def _draw_polygon(frame, pts, color=(0, 0, 255), thickness=2):
        arr = np.array([pts], dtype=np.int32)
        cv2.polylines(frame, arr, isClosed=True, color=color, thickness=thickness)

    @staticmethod
    def _draw_ruler_and_roi(frame, roi, step: int = 100):
        if frame is None:
            return
        h, w = frame.shape[:2]
        for x in range(0, w, step):
            cv2.line(frame, (x, 0), (x, 10), (255, 255, 255), 1)
            cv2.putText(frame, str(x), (x+2, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        for y in range(0, h, step):
            cv2.line(frame, (0, y), (10, y), (255, 255, 255), 1)
            cv2.putText(frame, str(y), (15, y+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        x1, y1, x2, y2 = roi
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "x1,y1", (x1+5, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.putText(frame, "x2,y1", (x2-55, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.putText(frame, "x1,y2", (x1+5, y2+15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.putText(frame, "x2,y2", (x2-55, y2+15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
