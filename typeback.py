#!/usr/bin/python
"""
Player piano without restriction that you start in python.

Also, when you're done, control returns to the controlling terminal,
so you can continue working on your demo live if you so choose.
"""
import os
import pty
import select
import sys
import termios
import tty



def typeback(input_stream):
    pid, fd = pty.fork()
    if not pid:
        try:
            os.execv("/bin/bash", ["/bin/bash", "-l"])
        finally:
            os._exit(1)
    old_mask = _mask_stdin()
    try:
        _process_loop(fd, input_stream)
    finally:
        _restore_stdin(old_mask)

def _process_loop(pty_fd, input_stream):
    read_from_file = True
    stdin = sys.stdin.fileno()
    to_read = [stdin, pty_fd]
    to_write = [sys.stdout.fileno(), pty_fd]
    all_fds = to_read + to_write
    stdout_buf = []
    stdin_buf = []
    while True:
        read_ready, write_ready, exc_fds  = select.select(to_read, [],  
                                                          all_fds, 0)
        if exc_fds:
            print "Exec fds - done"
            return
        if read_ready:
            if pty_fd in read_ready:
                stdout_buf = _read_buffer(pty_fd, stdout_buf)
                if not stdout_buf:
                    # pty died
                    return
                stdout_buf = _write_buffer(sys.stdout.fileno(), stdout_buf)
            if stdin in read_ready:
                if read_from_file:
                    _eat_char(stdin)
                    char = input_stream.read(1)
                    if not char:
                        # out of characters in the file - switch back to
                        # stdin
                        read_from_file = False
                    os.write(pty_fd, char)
                else:
                    stdin_buf = _read_buffer(stdin, stdin_buf)
                    if not stdin_buf:
                        return
                    stdin_buf = _write_buffer(pty_fd, stdin_buf)
            

def _write_buffer(fd, buf):
    while buf:
        rc = os.write(fd, buf[0])
        if rc != len(buf[0]):
            buf[0] = buf[rc:]
            return buf
        buf = buf[1:]
    return []

def _read_buffer(fd, buf):
    try:
        new_data = os.read(fd, 4096)
    except OSError:
        return
    if not new_data:
        return
    return buf + [new_data]

def _eat_char(fd):
    os.read(fd, 1)

def _mask_stdin():
    """ 
    disable echo of stdin
    """
    stdin_fd = sys.stdin.fileno()
    old_mask = termios.tcgetattr(stdin_fd)
    new = old_mask[:]
    new[3] = new[3] & ~termios.ECHO # 3 == 'lflags'
    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, new)
    tty.setraw(stdin_fd)
    return old_mask


def _restore_stdin(old_mask):
    """ 
    restore stdin
    """
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_mask)

def main(argv):
    if len(argv) != 2:
        print "usage: %s [filename]" % argv[0]
        sys.exit(1)
    typeback(open(argv[1]))

if __name__ == '__main__':
    main(sys.argv)
