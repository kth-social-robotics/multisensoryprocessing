import zmq
import sys
import pika
import msgpack
import thread
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.plotly as py
import json
import plotly.tools as tls
from numpy.random import random
sys.path.append('../..')
from shared import MessageQueue


mq = MessageQueue('kinect-listener')

# define initial plotting stuff
target_gaze_dic = {}
time_gaze_dict = {}
old_rt_data = ""


def callback(_mq, get_shifted_time, routing_key, body):

    """

    :param _mq:
    :param get_shifted_time:
    :param routing_key:
    :param body: json object containg address of the 0MQ server and file type of sensor
    :return:
    """

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, unicode(''))
    s.connect(body.get('address'))
    while True:
        data = s.recv()
        msgdata, timestamp = msgpack.unpackb(data, use_list=False)
        update_gaze_target_counts(msgdata['GazeCoding'], timestamp)
        send_to_environment(msgdata['GazeCoding'], timestamp)
    s.close()  # do we need this?


def record_target_change(rt_data):
    global old_rt_data
    if rt_data != old_rt_data:
        gaze_change = True
    else:
        gaze_change = False
    old_rt_data = rt_data  # set previous data to new one


def send_to_environment(rt_data, timestamp):
    global mq
    global old_rt_data

    if rt_data != old_rt_data:
        # gaze_change = True
        participant = routing_key.rsplit('.', 1)[1]
        # kinect.append({'name': 'kinect-gaze', 'time': time.time()})
        mq.publish(
            exchange='environment',
            routing_key='kinect-gaze.data.{}'.format(participant),
            body={"target_gaze_dic": target_gaze_dic, "timestamp": timestamp}
        )
        print json.dumps({"target_gaze_dic": target_gaze_dic, "timestamp": timestamp})


def update_gaze_target_counts(rt_data, timestamp):

    """
    Update the counts of gaze targets.

    This may or may not include a timestamp.
    Note that the counts are accumulated continously
    over time and are note reset after some time or
    after a target was detected.

    :param rt_data: any (string expected)
        the target currently being gazed at
        (or any other common information we want to store
    :param timestamp: float
        the time (either from time.time() or other)
        when the event took place
    """

    # gaze_dic[rt_data] += 1 if rt_data in gaze_dic else 1
    if rt_data in target_gaze_dic:
        target_gaze_dic[rt_data] += 1
    else:
        target_gaze_dic[rt_data] = 1

    # update timestamps gaze dic
    time_gaze_dict[timestamp] = rt_data

    record_target_change(rt_data)


def plot_histogramme(_):

    """
    The data for the figures is not passed as parameter,
    but is taken directly from the corresponding variable
    (e.g. target_gaze_dic and time_gaze_dict)

    Note that the function does not return anything.
    This is not necessary, since the animation.FuncAnimation()
    function takes its output automatically (see below).

    :param _: [ignored]
        dummy parameter for fulfilling animation.FuncAnimation() requirements
    """

    # plt.cla()  # clear figure axes
    # # create a barplot (used as histogram) with the gaze data
    # plt.bar(np.arange(len(target_gaze_dic.keys())), target_gaze_dic.values(), color='blue')
    # # give meaningful tick-labels on the x-axis
    # plt.xticks(range(len(target_gaze_dic)), target_gaze_dic.keys())


    # --- experimental time/gaze plot ---



    Y_AXIS = time_gaze_dict.values()
    # print time_gaze_dict.values()
    yTickMarks = time_gaze_dict.values()
    y = [yTickMarks.index(i) for i in Y_AXIS]
    # print y
    # plt.scatter(time_gaze_dict.keys(), y)
    # plt.yticks(range(len(set(time_gaze_dict.values()))), time_gaze_dict.values())

    # print set(time_gaze_dict.values()), time_gaze_dict.values, time_gaze_dict.keys
    colors = ['b', 'c', 'y', 'm', 'r']

    #for id in range(len((set(time_gaze_dict.values())))):
       # lo = plt.scatter(time_gaze_dict.keys(),1, marker='x', color=colors[id])

    #print time_gaze_dict.values()#, time_gaze_dict.keys()

    lo = plt.scatter(time_gaze_dict.keys(), y, marker='x', color=colors[0])

    #mpl_fig = plt.gcf()
    #plotly_fig = tls.mpl_to_plotly(mpl_fig)

    #plotly_fig['layout']['showlegend'] = True
    #spy.plot(plotly_fig)

    #py.plot(time_gaze_dict)

    # --- END experimental time/gaze plot ---


def listen():

    """
    Listen to queues relevant to Kinect data.
    """

    global mq
    mq.bind_queue(exchange='sensors', routing_key='kinect.new_sensor.*', callback=callback)

    print('[*] Waiting for messages. To exit press CTRL+C')
    mq.listen()


# threading magic (needed because start_consuming() blocks the main thread)
thread.start_new_thread(listen, ())

# main plotting-animation thread (must be on main thread)
fig = plt.figure()
animation = animation.FuncAnimation(fig, plot_histogramme, 10)
plt.show()
