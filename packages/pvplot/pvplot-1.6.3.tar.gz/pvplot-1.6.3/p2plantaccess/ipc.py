"""Simple IPC Message Queue class for Python3, using ctypes and libc.
"""
#Adopted from: https://gist.github.com/unautre/3cf4e9924ee81b762f82
__version__ = '1.0.0 2024-04-21'# Transport is static class
#TODO: Currently ftok file does not matter. Issue: if send size is bigger than recv buffer then queue will be spoiled. Ideally it should contain the max size of the receiver buffer.

"""```````````````````Usage
$ python3 parmhost/ipc.py -l
$ python3
from parmhost.ipc import Transport
msq = Transport()
msq.send(b'hello')
"""
import sys

from ctypes import CDLL, get_errno, create_string_buffer
from ctypes import c_ushort, c_int, c_uint, c_long, c_ulong
from ctypes import c_char_p, c_void_p, POINTER, Structure, cast

# we load the libc.
libc = CDLL("libc.so.6")
# define some consts.
IPC_CREAT = 0o1000
IPC_EXCL  = 0o2000
IPC_NOWAIT= 0o4000
IPC_RMID = 0
IPC_SET = 1
IPC_STAT = 2
IPC_INFO = 3
# typedef some types
key_t = c_int

# Static key for IPC    
ftok = libc.ftok
ftok.argtypes = [c_char_p, c_int]
ftkey = ftok(c_char_p(b"/tmp/ipcbor.ftok"), c_int(65))
if ftkey == -1:
    print("ERR: Could not create IPC Message Key, Please do: 'touch  /tmp/ipcbor.ftok'")
    sys.exit(1);
print(f'IPC ftok: {ftkey}')

class ipc_perm(Structure):
    _fields_ = [    ("__key", key_t),
            ("uid", c_uint),
            ("gid", c_uint),
            ("cuid", c_uint),
            ("cgid", c_uint),
            ("mode", c_ushort),
    ]

class msqid_ds(Structure):
    _fields_ = [    ("msg_perm", ipc_perm),
            ("msg_stime", c_ulong),
            ("msg_rtime", c_ulong),
            ("msg_ctime", c_ulong),
            ("__msg_cbytes", c_ulong),
            ("msg_qnum", c_ulong), # Useful:number of messages in queue
            ("msg_qbytes", c_ulong),
            ("msg_lspid", c_int),
            ("msg_lrpid", c_int)
    ]

class Transport:
    """Static class"""
    msgget = libc.msgget
    msgget.argtypes = [key_t, c_int]
    
    msgsnd = libc.msgsnd
    msgsnd.argtypes = [c_int, c_char_p, c_ulong, c_int]
    
    msgctl = libc.msgctl
    msgctl.argtypes = [c_int, c_int, POINTER(msqid_ds)]
    
    msgrcv = libc.msgrcv
    msgrcv.argtypes = [c_int, c_char_p, c_ulong, c_ulong, c_int]
    
    perror = libc.perror
    perror.argtypes = [c_char_p]
    
    def init(key=ftkey, mode=IPC_CREAT | 0o644, bitrate=None):
        Transport.id_rcv = Transport.msgget(key+1, mode)
        Transport.id_snd = Transport.msgget(key, mode)
        print(f'IPC id_rcv: {Transport.id_rcv}, id_snd: {Transport.id_snd}')

    def send(msg):#, msglen), msgtype=1, flag=0):
        msgtype=1; flag=0
        msglen = len(msg)
        buf = create_string_buffer(msglen+8)
        lbuf = cast(buf, POINTER(c_long))
        lbuf[0] = msgtype
        buf[8:] = msg[:msglen]
        r = Transport.msgsnd(Transport.id_snd, buf, msglen, flag)
        if r != 0:
            raise BufferError('in Transport.send.')
            msq.clear()

    def recv(msgsize=15000):
        msgtype=1; flag=0
        size = msgsize+8
        buf = create_string_buffer(size)
        msglen = Transport.msgrcv(Transport.id_rcv, buf, size, msgtype, flag)
        # do not return type
        #lbuf = cast(buf, POINTER(c_long)) # for msgtype        
        #return lbuf.contents.value, buf[8:msglen+8]
        return buf[8:msglen+8]

    def clear():
        Transport.msgctl(Transport.id_rcv, IPC_RMID, None)
        Transport.msgctl(Transport.id_snd, IPC_RMID, None)
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__
        ,formatter_class=argparse.ArgumentDefaultsHelpFormatter
        ,epilog=f'ipc {__version__}')
    parser.add_argument('-l','--listener', action='store_true', help=\
    'Print incoming messages')
    parser.add_argument('messages', nargs='*', help='Messages to send to server')
    pargs = parser.parse_args()

    msq = Transport()
    for msg in pargs.messages:
        msq.send(msg)
    
    if pargs.listener:
        print('IPC Listening')
        msglen = 1
        while msglen > 0:
           msg = msq.recv()
           print(f'IPC Received {msglen} bytes:`{msg}`')
           msglen = len(msg)
        msq.clear()
        
