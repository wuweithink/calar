#!/usr/bin/env python3


"""G920 device control test"""
from controldevice import G920ControlDevice


#This code is only for test!
def main():
    dev_thread = G920ControlDevice()
    dev_thread.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone')
