from collections import namedtuple

class BackendUnavailableError(Exception): pass
class NoBackendsFoundError(Exception): pass
class DeviceNotFoundError(Exception): pass


Keystate = namedtuple('Keystate', ['up', 'right', 'left', 'down', 'ok', 'window', 'back', 'light', 'menu'])


def parse_keystate(state):
    keystate = Keystate(
        up=(state & 0x8000) > 0,
        right=(state & 0x1000) > 0,
        left=(state & 0X2000) > 0,
        down=(state & 0x4000) > 0,
        ok=(state & 0x0800) > 0,
        window=(state & 0x0400) > 0,
        back=(state & 0x0200) > 0,
        light=False,
        menu=(state & 0x0100) > 0
    )
    return keystate


class PyUsbBackend(object):
    try:
        import usb
        available = True
    except ImportError:
        available = False

    def __init__(self, idVendor, idProduct):
        if not self.available:
            raise BackendUnavailableError('PyUSB backend not available')
        self._init_usb(idProduct, idVendor)

    def _init_usb(self, idVendor, idProduct):
        self.dev = self.usb.core.find(idVendor=idVendor, idProduct=idProduct)
        if self.dev is None:
            raise DeviceNotFoundError('SpacePilot Pro device not found')

        try:
            self.dev.set_configuration()
        except self.usb.USBError as err:
            if err.errno != 16:
                raise

        self.interface = self.dev.configurations()[0].interfaces()[0]
        self.keys_in = self.interface.endpoints()[0]
        self.lcd_out = self.interface.endpoints()[1]

    def read_keystate(self, timeout=None):
        try:
            keystate_raw = self.keys_in.read(2, timeout)
        except self.usb.USBError as err:
            if err.errno != 110:
                raise
            return None

        keystate = int(keystate_raw[0]) << 8 + int(keystate_raw[1])
        return parse_keystate(keystate)

    def write_display(self, frame):
        if not isinstance(frame, bytes):
            raise TypeError('frame needs to be a byte string')

        self.lcd_out.write(frame)


def get_usb_backend(backend):
    backends = {
        'pyusb': PyUsbBackend
    }

    available = {name: b.available for (name, b) in backends.items() if b.available}
    if not available:
        raise NoBackendsFoundError('No supportd backends found')

    if backend is not None:
        if backend not in backends:
            raise BackendUnavailableError('Backend {} is unknown'.format(backend))
    else:
        backend = tuple(available.keys())[0]

    return backends[backend]