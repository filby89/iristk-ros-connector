#!/usr/bin/env python

import rospy
import socket
import sys
import numpy as np
import ast
from std_msgs.msg import String


class IrisTK_Bridge(object):
    """docstring for IrisTK_Bridge"""
    def __init__(self, broker_ip, broker_port, ticket_name, iristk_name, ros_node_name):
        super(IrisTK_Bridge, self).__init__()
        self.ticket_name = ticket_name
        self.iristk_name = iristk_name
        self.ros_node_name = ros_node_name
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_broker()
        self.init_ros_and_wait_for_iristk_messages()


    def connect_to_broker(self):
        self.sock.connect((self.broker_ip, self.broker_port))

        msg = 'CONNECT %s %s \n' % (self.ticket_name, self.iristk_name)
        
        self.sock.send(msg)

        # 10 is a random num
        data = self.sock.recv(10)

        # subscribe to the event we want. In this case we only listen for athena.sloc.** events. ** is a wildcard
        self.sock.sendall('SUBSCRIBE athena.sloc.** \n')

        print "SUCCESSFULLY SUBSCRIBED TO BROKER"

    # read line from socket
    def readlines(self, sock, recv_buffer=4096, delim='\n'):
        buffer = ''
        data = True
        while data:
            data = sock.recv(recv_buffer)
            buffer += data

            while buffer.find(delim) != -1:
                line, buffer = buffer.split('\n', 1)
                yield line
        return


    def send_message(self, event_name, text):
        json_format = "{ \"class\": \"iristk.system.Event\", \"event_sender\": \"%s\" , \"event_name\": \"%s\", \"text\": \"%s\" }\n"
        event_format = "EVENT {event_name} {byte_size}\n"

        j =  json_format % (self.iristk_name, event_name, text)
        # len is to get bytes in python 2.X
        full_event = event_format.format(event_name=event_name, byte_size=len(j))
        self.sock.sendall(full_event)
        self.sock.sendall(j)
        print "Sent event %s with json info %s" % (full_event, j)


    def init_ros_and_wait_for_iristk_messages(self):
        pub = rospy.Publisher("sample_topic_name", String, queue_size=10)
        rospy.init_node(self.ros_node_name, anonymous=True)

        while not rospy.is_shutdown():
            for line in self.readlines(self.sock):
                pass
                # maybe send a message to iristk
                self.send_message("event_name", "something_happened")
                #maybe publish something to ros
                pub.publish("something")
                    


if __name__ == '__main__':
    ##### customizable parameters #####
    ticket_name = 'furhat' # ticket name
    iristk_name = 'NAME_IN_IRISTK' # name of the system in iristk 
    ip = '192.168.0.114' # broker ip
    port = 1932 # broker port
    ros_node_name = 'ros_node_name'
    ###################################

    bridge = IrisTK_Bridge(ip,port,ticket_name,iristk_name,ros_node_name)
