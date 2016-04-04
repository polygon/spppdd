class BackendUnavailableError(Exception): pass
class NoBackendsFoundError(Exception): pass
class DeviceNotFoundError(Exception): pass


class UsbBackend(object):
    def __init__(self, idVendor: int, idProduct: int):
        raise NotImplementedError('Use implementations of UsbBackend')

    def read_keystate(self, timeout: int or None=None) -> int or None:
        """
        Reads the keystate from the interrupt endpoint

        This function reads the next key event from the interrupt endpoint.
        It should be called often since only a limited number (in my case two)
        of events are buffered.

        This function will block until an event is read or the timeout
        is reached in which case it returns None.

        The keystate is returned as an uint16 bitfield.
        @param timeout: Timeout in milliseconds
        @return: uimt16 bitfield with button states or None when timed out
        """
        raise NotImplementedError('Use implementations of UsbBackend')

    def write_display(self, frame: bytes) -> None:
        """
        Write data frame to the LCD bulk endpoint

        Raw function that accepts and data length.
        @param frame: Data frame to write
        @return: None
        """
        raise NotImplementedError('Use implementations of UsbBackend')


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
        return keystate

    def write_display(self, frame):
        if not isinstance(frame, bytes):
            raise TypeError('frame needs to be a byte string')

        self.lcd_out.write(frame)


def get_usb_backend(backend=None):
    """
    Returns the USB backend class

    Returns the requested backend if available. Returns the first available
    backend if no specific one is requested.
    @param backend: Name of the specific required backend
    @return: UsbBackend derived class
    """
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