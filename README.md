# spppdd
SPace Pilot Pro Display Driver

## About
SPacePilotProDisplayDriver, or SPPPDD for short, is a python library to interface the 320x240 5-6-5 16Bit RGB LCD Display built in the 3D Connexion SpacePilot Pro.

Thanks to https://github.com/MultiCoreNop/Logitech-G19-Linux-Daemon for reverse engineering the header.

## Requirements
The following is for a Debian Jessie based system. So your mileage may vary on this steps.

Make sure your SpacePilot Pro is plugged in. Try `lsusb`, it should show somethine like this:
    > Bus 002 Device 003: ID 046d:c629 Logitech, Inc.

To be able to make the device writeable by the user, you should create a udev rule for your SpacePilot Pro.
You can take the following example and write it to something like `/etc/udev/rules.d/90-spacepilotpro.udev`:
   ```
    # Allow userspace access to SpacePilot Pro for plugdev members
    ATTR{idVendor}=="046d", ATTR{idProduct}=="c629", MODE="660", GROUP="plugdev"
   ```

This code should also work with the Logitech Display build in the [WP: Logitech G19](https://en.wikipedia.org/wiki/Logitech_G19) and alike keyboards or any other device with this kind of Logitech Screen (320x240, 5-6-5 16 Bit RGB). So you might want to change this values above accordingly and also use make sure to use this values in the code as well: [spppdd.py](spppdd/spppdd.py).

Make sure your user is a member of plugdev with `$ groups $USER`.
You can add yourself with `$ sudo useradd $USER plugdev`

## Requirements
python3 (maybe works on python2.7, not tested though)
pyusb
numpy

## Usage
See [spppdd/executables/](executables/).
