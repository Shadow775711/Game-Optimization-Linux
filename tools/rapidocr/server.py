from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from rapidocr import RapidOCR
import cv2
import numpy as np
import json
import time
import threading

ocr = RapidOCR(params={
    "EngineConfig.onnxruntime.intra_op_num_threads": 4,
    "EngineConfig.onnxruntime.inter_op_num_threads": 1,
    "Global.use_det": False,
    "Global.use_cls": False,
})
lock = threading.Lock()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health":
            self.send_error(404)
            return
        self.reply({"status": "ok", "engine": "RapidOCR"})

    def do_POST(self):
        if self.path != "/ocr":
            self.send_error(404)
            return

        size = int(self.headers.get("Content-Length", "0"))
        if not 0 < size < 10000000:
            self.send_error(400)
            return

        data = self.rfile.read(size)
        image = cv2.imdecode(
            np.frombuffer(data, dtype=np.uint8),
            cv2.IMREAD_COLOR
        )
        if image is None:
            self.send_error(400)
            return

        start = time.monotonic()
        h, w = image.shape[:2]

        x1 = round(w * 380 / 1536)
        x2 = round(w * 1150 / 1536)
        y1 = round(h * 90 / 210)
        y2 = round(h * 145 / 210)

        crop = image[y1:y2, x1:x2]
        if crop.size == 0:
            self.send_error(400)
            return

        crop = cv2.resize(
            crop, None,
            fx=2, fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        with lock:
            result = ocr(crop)

        texts = []
        if result.txts:
            for text, score in zip(result.txts, result.scores):
                text = str(text).strip()
                score = float(score)

                if (
                    score < 0.75
                    or len(text.split()) < 3
                    or sum(c.isalpha() for c in text) < 8
                ):
                    continue

                texts.append({
                    "text": text,
                    "confidence": score,
                    "box": [
                        [x1, y1],
                        [x2, y1],
                        [x2, y2],
                        [x1, y2]
                    ]
                })

        self.reply({
            "results": texts,
            "elapsed_ms": round(
                (time.monotonic() - start) * 1000, 1
            )
        })

    def reply(self, payload):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass

print("RapidOCR gotowy: http://127.0.0.1:8765", flush=True)
ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
