import cv2


class CameraManager:
    def __init__(self, camera_index=0, width=640, height=480, mirror=True):
        self.camera_index = int(camera_index)
        self.width = int(width)
        self.height = int(height)
        self.mirror = bool(mirror)
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap.release()
            self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            self.release()
            raise RuntimeError(
                f"Could not open camera index {self.camera_index}. Connect a webcam "
                "or an iPhone virtual webcam, then adjust camera_index in config.json."
            )
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        ok, frame = self.cap.read()
        if not ok or frame is None:
            self.release()
            raise RuntimeError("Camera opened but did not provide a frame. Check camera access.")

    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        ok, frame = self.cap.read()
        if not ok or frame is None:
            return False, None
        if self.mirror:
            frame = cv2.flip(frame, 1)
        return True, frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()
