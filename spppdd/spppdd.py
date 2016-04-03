from . usb_backend import get_usb_backend

from array import array
import numpy as np

class NoUSBBackendError(Exception): pass

class SPPPDD(object):
    def __init__(self, idVendor=None, idProduct=None, backend=None):
        self.idVendor = idVendor if idVendor is not None else 0x046d
        self.idProduct = idProduct if idProduct is not None else 0xc629
        self.usb_backend = get_usb_backend(backend)
        self.usb = self.usb_backend(self.idProduct, self.idVendor)

    def write_screen_raw(self, data):
        """
        Writes a raw frame to the screen

        Expects a bytestring of exactly 153600 bytes corresponding to
        a 320x240x2 image.

        The pixel format used is 5-6-5 16-Bit RGB.
        """

        if not isinstance(data, bytes):
            raise TypeError('Data must be of type bytes')
        if len(data) != 153600:
            raise ValueError('Data must be 153600 bytes long')

        header1 = array('B', [0x10, 0x0F, 0x00, 0x58, 0x02, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x3F, 0x01, 0xEF, 0x00, 0x0F]).tobytes()
        header2 = array('B', [a for a in range(16, 256)]).tobytes()
        header3 = array('B', [a for a in range(256)]).tobytes()

        frame = header1 + header2 + header3 + data
        self.usb.write_display(frame)

    def write_screen_numpy(self, image):
        if not isinstance(image, np.ndarray):
            raise TypeError('image must be a numpy array')
        if image.shape != (320, 240, 3):
            raise TypeError('image must have shape (320, 240, 3)')

        if image.dtype == np.float:
            clamped = np.clip(image, 0.0, 1.0)
            conv = (clamped * np.array([31., 63., 31.])).astype(np.uint8)
        elif image.dtype == np.uint8:
            conv = np.right_shift(image, [3, 2, 3])
        else:
            raise TypeError('image must be of type np.float or np.uint8')

        packed = np.left_shift(conv, [11, 5, 0]).sum(2).flatten().astype(np.uint16)
        self.write_screen_raw(packed.tobytes())