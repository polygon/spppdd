from . usb_backend import get_usb_backend

from array import array
import numpy as np
from collections import namedtuple

class NoUSBBackendError(Exception): pass

class SPPPDD(object):
    def __init__(self, idVendor: int or None=None, idProduct: int or None=None, backend: str or None=None):
        """
        Creates a SPace Pilot Pro Display Driver object

        Use idVendor and idProduct to override default values
        and backend to select a specific USB backend.

        Currently, only the 'pyusb' backend is available.
        @param idVendor: Override default idVendor=0x046d
        @param idProduct: Override default idProduct=0xc629
        @param backend: Name of backend to use
        """
        self.idVendor = idVendor if idVendor is not None else 0x046d
        self.idProduct = idProduct if idProduct is not None else 0xc629
        self.usb_backend = get_usb_backend(backend)
        self.usb = self.usb_backend(self.idProduct, self.idVendor)

    def write_screen_raw(self, data: bytes) -> None:
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

    def write_screen_numpy(self, image: np.ndarray) -> None:
        """
        Convert a numpy array and write it to the screen

        Converts a (320, 240, 3)-shaped numpy array to the display format and
        sends it to the display.

        If the dtype of the image is float it is assumed to be RGB data
        in the range [0., 1.] and the input is clamped to these values.

        If the dtype of the image is uint8 it is assumed to be RGB data
        in the range [0, 255] and the lowest bits are discarded during conversion.

        Other dtypes are not supported yet.
        @param image: numpy.ndarray of shape (320, 240, 3)
        """
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
            raise TypeError('image must be an numpy.ndarray of type npumpy.float or numpy.uint8')

        packed = np.left_shift(conv, [11, 5, 0]).sum(2).flatten().astype(np.uint16)
        self.write_screen_raw(packed.tobytes())


Keystate = namedtuple('Keystate', ['up', 'right', 'left', 'down', 'ok', 'window', 'back', 'light', 'menu'])


def parse_keystate(keystate: int) -> Keystate:
    """
    Parses an uint16 keystate bitfield into a Keystate tuple

    Tuple values are booleans indicating button states.
    @param keystate: uint16 keystate bitfield
    @return: Keystate tuple
    """
    keystate_tuple = Keystate(
        up=(keystate & 0x8000) > 0,
        right=(keystate & 0x1000) > 0,
        left=(keystate & 0X2000) > 0,
        down=(keystate & 0x4000) > 0,
        ok=(keystate & 0x0800) > 0,
        window=(keystate & 0x0400) > 0,
        back=(keystate & 0x0200) > 0,
        light=False,
        menu=(keystate & 0x0100) > 0
    )
    return keystate_tuple