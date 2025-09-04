"""Access to P2Plant process variables with IPC queue link.
Usage:
$ python3
from p2plantaccess import Access as pa
pa.init(); pa.start()
pa.request(["info", ["*"]])
pa.request(["get", ['run',"version"]])
  or:
pa.request('["get", ["run","version"]]')
pa.request(['set', [('run','stop')]])
"""
__version__ = 'v1.0.4 2025-02-17'# recv blocking is bool
print(f'p2plantAccess {__version__}')

import time
import threading
from collections import deque
import numpy as np
from json import loads
import cbor2 as cbor
#import cbor

dtype = {# map of CBOR tags to numpy dtype
    72: "int8",
    64: "uint8",
    69: "uint16",
    77: "int16",
    78: "int32",
    70: "uint32",
}
tag = {v:k for k,v in dtype.items()}# map of dtype to CBOR tag

def printi(msg): print(f'inf_p2pa: {msg}')
def printw(msg): print(f'WAR_p2pa: {msg}')
def printe(msg): print(f'ERR_p2pa: {msg}')
def printv(msg):
    if (Access.DBG): print(f'dbg_p2p: {msg}')

class Access:
    """Static class"""
    DBG = False
    receivedList = []
    commandReply = deque()# OCould keep many deliveries
    subscriptionReply = deque()# Only one delivery could be kept here
    started = False
    receivedMap = {}

    event_subscription_received = threading.Event()
    event_reply_received = threading.Event()
    
    queueAndEvents = {
    'reply': (commandReply, event_reply_received),# event_reply_processed),
    'subscription': (subscriptionReply, event_subscription_received),# event_subscription_processed)
    }

    def init(transport='ipc', bitrate=7372800):
        if transport== 'ipc':
            from .ipc import Transport
        Transport.init(bitrate=bitrate)
        Access.transport = Transport

    def start():
        thread = threading.Thread(target=Access._receiver, daemon=True)
        Access.started = True
        thread.start()

    def stop():
        Access.started = False

    def _receiver():
        printi("Receiver started")
        while Access.started:
            bbuf = Access.transport.recv()
            printv(f'Received a message[{len(bbuf)}]: {bbuf}')
            Access.receivedList = cbor.loads(bbuf)
            if len(Access.receivedList) > 0\
              and Access.receivedList[0] == 'Subscription':
                printv(f'Subscriptions: {Access.receivedList}')
                if len(Access.subscriptionReply) > 0:
                    continue
                Access.subscriptionReply.append(Access.receivedList[1:])
                Access.event_subscription_received.set()
            else:
                Access.commandReply.append(Access.receivedList)
                Access.event_reply_received.set();
        printi("Receiver finished")

    def send(request):
        """Encode object to CBOR and send it to IPC queue"""
        if not Access.started:
            printw("Receiver is not started")
            return 
        #cborobj = cbor.dumps(request, canonical=True)# expect more compact output, but it is not compatible with p2plant.
        cborobj = cbor.dumps(request)
        #print(f'send cbor: {cborobj}')
        Access.transport.send(cborobj)
        #print('')

    #def array(nparray):
    #    """Convert numpy array to CBORTag. For use in send()."""
    #    atag = tag[str(nparray.dtype)]
    #    return cbor.CBORTag(atag, nparray.tobytes())

    def recv(what:str = 'reply', blocking=True):
        """Receive data, the what could be 'reply' or 'Subscription'.
        if blocking==True, the program will be blocked until arrival of 
        new data"""
        #print(f'recv {what}, {blocking}')
        if not Access.started:
            printw("Receiver is not started")
            return
        try:
            queue, evRcv = Access.queueAndEvents[what]
        except:
            return {'ERR':f'recv supports only {Access.queueAndEvents.keys()}'}
        if blocking:
            evRcv.wait()
        else:
            if not evRcv.is_set():
                return {}
        l = len(queue)
        printv(f'reply received {what}[{l}]')
        Access.receivedMap = {}
        if l == 0:
            return []
        if l == 1:# Handling last item. The flag could be cleared.
            evRcv.clear()
        qitem = deque(queue.pop())
        printv(f'qitem: {qitem}')
        if (len(qitem)%2) != 0:
            # Received odd number of items: that happens if request was incorrect.
            printe(f'Request was not recognized by server: {qitem[0]}')
            return {}
        try:
            while par := qitem.popleft():
                parmap = qitem.popleft()
                if par in Access.receivedMap:
                   Access.receivedMap[par].update(parmap)
                else:
                    Access.receivedMap[par] = parmap
        except IndexError:
            pass
        #print(f'Access.receivedMap: {Access.receivedMap}')
        return Access.receivedMap

    def decode(parName='*'):
        """Translate reply to standard python objects""" 
        outmap = {}
        inmap = Access.receivedMap
        if parName != '*':
            try:
                inmap = {parName: Access.receivedMap[parName]}
            except:
                return {}
        for par,parmap in inmap.items():
            outmap[par] = {}
            for key,v in parmap.items():
                if isinstance(v, cbor.CBORTag):
                    v = np.frombuffer(v.value, dtype[v.tag])
                    if key == 'v':
                        shape = parmap.get('shape')
                        v = v.reshape(shape)
                    elif key == 't':
                        v = v[0],v[1]
                outmap[par][key] = v
        return outmap

    def valueAndTimestamp(parName:str):
        """Return (value,timestamps) of a parameter"""
        try:
            parmap = Access.decode(parName)[parName]
            v,t = parmap['v'],parmap['t']
            return (v,t)
        except:
            return []

    def request(obj):
        """Send object or text to IPC queue and receive/decode the reply"""
        if isinstance(obj, str):
            try:
                obj = loads(obj)
            except Exception as e:
                printe(f"Failed to encode string '{obj}' to json: {e}")
                return {}
        try:
            printv(f'Sending obj: {obj}')
            Access.send(obj)
            Access.recv()
            r = Access.decode()
            printv(f'rcv: {r}')
            return r
        except Exception as e:
            printe(f'Sending {obj}: {e}')
            return {}
