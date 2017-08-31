#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

""" Video Syncing with Gaze data overlay
"
" This example uses the video as a main source to sync eyetracking data. Since the
" video is the main source the eyetracking data will be synced on the videos output.
"
" Eyetracking data is read directly into eyetracking data queues (one sync and one data)
"
" When a video pts is detected on the incoming data it is added with the buffer
" offset.
"
" When a video is about to be displayed its offset is matched with the offset
" in the video pts queue to get the corresponding pts. With this pts we can
" calculate the pts sync point in the eyetracking data and present the
" yetracking points that corresponds to this pts. For frames without pts we
" move eyetracking data forward using the video frame timestamps.
"
" This code does not do calibration and it does not compensate to place the
" gazepoint in the absolute center of the string "*" but rather it is the start
" of the "*" string position.
"
" Note: This example program is *only* tested with Python 2.7 on Ubuntu 12.04 LTS  
"       and Ubuntu 14.04 LTS (running natively).
"""

# Standard libraries. We need socket for socket communication and json for
# json parsing
import socket
import json

# GStreamer integration. We need glib for main loop handling and gst for
# gstreamer video.
try:
    import glib
    import gst
except ImportError:
    print "Please make sure you have glib and gst python integration installed"
    raise


def mksock(peer):
    """ Create a socket pair for a peer description """
    iptype = socket.AF_INET
    if ':' in peer[0]:
        iptype = socket.AF_INET6
    return socket.socket(iptype, socket.SOCK_DGRAM)

class KeepAlive:
    """ Sends keep-alive signals to a peer via a socket """
    _sig = 0
    def __init__(self, sock, peer, streamtype, timeout=1):
        jsonobj = json.dumps({
            'op' : 'start',
            'type' : ".".join(["live", streamtype, "unicast"]),
            'key' : 'anything'})
        sock.sendto(jsonobj, peer)
        self._sig = glib.timeout_add_seconds(timeout, self._timeout, sock, peer, jsonobj)

    def _timeout(self, sock, peer, jsonobj):
        sock.sendto(jsonobj, peer)
        return True

    def stop(self):
        glib.source_remove(self._sig)


class BufferSync():
    """ Handles the buffer syncing
    "
    " When new eyetracking data arrives we store it in a et queue and the 
    " specific eyetracking to pts sync points in a et-pts-sync queue.
    "
    " When MPegTS is decoded we store pts values with the decoded offset in a
    " pts queue.
    "
    " When a frame is about to be displayed we take the offset and match with
    " the pts from the pts queue. This pts is then synced with the
    " et-pts-sync queue to get the current sync point. With this sync point
    " we can sync the et queue to the video output.
    "
    " For video frames without matching pts we move the eyetracking data forward
    " using the frame timestamps.
    " 
    """
    _et_syncs = []      # Eyetracking Sync items
    _et_queue = []      # Eyetracking Data items
    _et_ts = 0          # Last Eyetraing Timestamp
    _pts_queue = []     # Pts queue
    _pts_ts = 0         # Pts timestamp

    def __init__(self, cb):
        """ Initialize a Buffersync with a callback to call with each synced
        " eyetracking data
        """
        self._callback = cb

    def add_et(self, obj):
        """ Add new eyetracking data point """
        # Store sync (pts) objects in _sync queue instead of normal queue
        if 'pts' in obj:
            self._et_syncs.append(obj)
        else:
            self._et_queue.append(obj)

    def sync_et(self, pts, timestamp):
        """ Sync eyetracking sync datapoints against a video pts timestamp and stores
        " the frame timestamp
        """
        # Split the gaze syncs to ones before pts and keep the ones after pts
        syncspast = filter(lambda x: x['pts'] <= pts, self._et_syncs)
        self._et_syncs = filter(lambda x: x['pts'] > pts, self._et_syncs)
        if syncspast != []:
            # store last sync time in gaze ts and video ts
            self._et_ts = syncspast[-1]['ts']
            self._pts_ts = timestamp

    def flush_et(self, timestamp):
        """ Flushes synced eyetracking on video
        " This calculates the current timestamp with the last gaze sync and the video
        " frame timestamp issuing a callback on eyetracking data that match the
        " timestamps.
        """
        nowts = self._et_ts + (timestamp - self._pts_ts)
        # Split the eyetracking queue into passed points and future points
        passed = filter(lambda x: x['ts'] <= nowts, self._et_queue)
        self._et_queue = filter(lambda x: x['ts'] > nowts, self._et_queue)
        # Send passed to callback
        self._callback(passed)

    def add_pts_offset(self, offset, pts):
        """ Add pts to offset queue """
        self._pts_queue.append((offset, pts))

    def flush_pts(self, offset, timestamp):
        """ Flush pts to offset or use timestamp to move data forward """
        # Split pts queue to used offsets and past offsets
        used = filter(lambda x: x[0] <= offset, self._pts_queue)
        self._pts_queue = filter(lambda x: x[0] > offset, self._pts_queue)
        if used != []:
            # Sync with the last pts for this offset
            self.sync_et(used[-1][1], timestamp)
        self.flush_et(timestamp)


class EyeTracking():
    """ Read eyetracking data from RU """
    _ioc_sig = 0
    _buffersync = None
    def start(self, peer, buffersync):
        self._sock = mksock(peer)
        self._keepalive = KeepAlive(self._sock, peer, "data")
        ioc = glib.IOChannel(self._sock.fileno())
        self._ioc_sig = ioc.add_watch(glib.IO_IN, self._data)
        self._buffersync = buffersync

    def _data(self, ioc, cond):
        """ Read next line of data """
        self._buffersync.add_et(json.loads(ioc.readline()))
        return True
   
    def stop(self):
        """ Stop the live data """
        self._keepalive.stop()
        self._sock.close()
        glib.source_remove(self._ioc_sig)
        

class Video():
    """ Video stream from RU """
    _PIPEDEF=[
        "udpsrc name=src blocksize=1316 closefd=false buffer-size=5600", # UDP video data
        "tsparse",                      # parse the incoming stream to MPegTS
        "tsdemux emit-stats=True",      # get pts statistics from the MPegTS stream
        "queue",                        # build queue for the decoder 
        "ffdec_h264 max-threads=0",     # decode the incoming stream to frames
        "identity name=decoded",        # used to grab video frame to be displayed
        "textoverlay name=textovl text=* halignment=position valignment=position xpad=0  ypad=0", # simple text overlay
        "xvimagesink force-aspect-ratio=True name=video" # Output on XV video
    ]
    _pipeline = None    # The GStreamer pipeline
    _textovl = None     # Text overlay element
    _keepalive = None   # Keepalive for video
    _sock = None        # Communicaion socket

    def draw_gaze(self, objs):
        """ Move gaze point on screen """
        # Filter out gaze points. Gaze comes in higher Hz then video so there
        # should be 1 to 3 gaze points for each video frame
        objs = filter(lambda x: 'gp' in x, objs)
        if len(objs) > 3:
            print "Drop %d" % len(objs)
        if len(objs) == 0:
            return
        obj = objs[-1]
        if 'gp' in obj and obj['gp'][0] != 0 and obj['gp'][1] != 0:
            self._textovl.set_property("xpos", obj['gp'][0])
            self._textovl.set_property("ypos", obj['gp'][1])

    def start(self, peer, buffersync):
        """ Start grabbing video """
        # Create socket and set syncbuffer
        self._sock = mksock(peer)
        self._buffersync = buffersync

        # Create pipeline
        self._pipeline=gst.parse_launch(" ! ".join(self._PIPEDEF))

        # Add watch to pipeline to get tsdemux messages
        bus = self._pipeline.get_bus()
        bus.add_watch(self._bus)

        # Set socket to get data from out socket
        src = self._pipeline.get_by_name("src")
        src.set_property("sockfd", self._sock.fileno())
        
        # Catch decoded frames
        decoded = self._pipeline.get_by_name("decoded")
        decoded.connect("handoff", self._decoded_buffer)
        
        # Store overlay object
        self._textovl = self._pipeline.get_by_name("textovl")
        
        # Start video streaming
        self._keepalive = KeepAlive(self._sock, peer, "video")
        
        # Start the video pipeline
        self._pipeline.set_state(gst.STATE_PLAYING)
        
    def _bus(self, bus, msg):
        """ Buss message handler 
        " We only collect pts-offset pairs
        """
        if msg.type == gst.MESSAGE_ELEMENT:
            st = msg.structure
            # If we have a tsdemux message with pts field then lets store it
            # for the render pipeline. Will be piced up by the handoff
            if st.has_name("tsdemux") and st.has_field("pts"):
                    self._buffersync.add_pts_offset(st['offset'], st['pts'])
        return True

    def _decoded_buffer(self, ident, buf):
        """ Callback for decoded buffer """
        # Make sure to convert timestamp to us 
        self._buffersync.flush_pts(buf.offset, buf.timestamp/1000)

    def stop(self):
        self._pipeline.set_state(gst.STATE_NULL)
        self._pipeline = None
        self._sock.close()
        self._sock = None
        self._keepalive.stop()
        self._keepalive = None

if __name__=="__main__":
    import sys
    if len(sys.argv) <= 1:
        print "Use %s [host|ip]" % sys.argv[0]
        exit(1)
    glib.threads_init()
    ml = glib.MainLoop();
    peer = (sys.argv[1], 49152)
    # Create Video and Gaze and BufferSync
    video = Video()
    et = EyeTracking()
    buffersync = BufferSync(video.draw_gaze)
    # Start video and gaze
    et.start(peer, buffersync)
    video.start(peer, buffersync)
    # Enter main loop
    ml.run()
        
        
