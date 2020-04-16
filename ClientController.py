#!/usr/bin/env python3
###############################################################################
import socket
import select
import re
import time
###############################################################################
from datetime import timedelta
###############################################################################


###############################################################################
class ClientController:

    ###########################################################################
    # Vars
    address = ""
    port = 0
    password = ""
    csocket = None
    ###########################################################################
    time_regex = re.compile(r'((?P<hours>\d+?) hours)? ?((?P<minutes>\d+?) mins)? ?((?P<seconds>\d+?) secs)?')
    ###########################################################################

    ###########################################################################
    def __init__(self, address='localhost', port=36330, password=None):
        self.address = address
        self.port = int(port)
        self.password = password
        #######################################################################
        self.__open()
    ###########################################################################

    ###########################################################################
    def __del__(self):
        self.__close()
    ###########################################################################

    ###########################################################################
    def __close(self):
        if(self.csocket is not None):
            try:
                self.csocket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.csocket.close()
            except Exception:
                pass
            self.csocket = None
    ###########################################################################

    ###########################################################################
    def __open(self):
        self.__reset()
        self.csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.csocket.connect((self.address, self.port))
        self.__read()
        if(self.password):
            self.send('auth "%s"' % self.password)
    ###########################################################################

    ###########################################################################
    def __reset(self):
        self.__close()
    ###########################################################################

    ###########################################################################
    def __can_read(self):
        rlist, wlist, xlist = select.select([self.csocket], [], [], 0)
        return len(rlist) != 0
    ###########################################################################

    ###########################################################################
    def __can_write(self):
        rlist, wlist, xlist = select.select([], [self.csocket], [], 0)
        return len(wlist) != 0
    ###########################################################################

    ###########################################################################
    def __get_type_count(self, type):
        type = self.__validate_type(type)
        if(type != 'all'):
            type = type.upper() + 's'
            return int(self.get_client_info('System', type))
    ###########################################################################

    ###########################################################################
    def __parse(self, message):
        start = message.find('\nPyON ')
        if(start == -1):
            return message.strip()[:-1]
        else:
            return self.__parse_pyon(message[start:])
    ###########################################################################

    ###########################################################################
    def __parse_pyon(self, message):
        eol = message.find('\n', 1)
        if(eol != -1):
            line = message[1:eol]
            tokens = line.split(None, 2)
            if(len(tokens) < 3):
                raise Exception(
                    'Invalid PyON line: %s' % line.encode('string_escape'))
            end = message.find('\n---\n')
            if(end != -1):
                data = message[eol + 1: end]
                if(tokens[2] == "error"):
                    raise Exception(data)
                try:
                    return eval(data, {}, {})
                except Exception as e:
                    raise Exception(
                        'ERROR parsing PyON message: %s: %s'
                        % (str(e), data.encode('string_escape')))
            else:
                raise Exception(
                    'Invalid PyON line: %s' % line.encode('string_escape'))
    ###########################################################################

    def __parse_time(self, time_str):
        parts = self.time_regex.search(time_str)
        if not parts:
            return
        parts = parts.groupdict()
        time_params = {}
        for name in parts:
            if(parts[name] is not None):
                time_params[name] = int(parts[name])
        return timedelta(**time_params)

    ###########################################################################
    def __read(self):
        full_buff = bytearray()
        buffer_size = 4096
        while True:
            local_buff = self.csocket.recv(buffer_size)
            buff_length = len(local_buff)
            if(buff_length > 0):
                full_buff.extend(local_buff)
            if(not self.__can_read()):
                break
        full_str = self.__parse(full_buff.decode('ASCII'))
        return full_str
    ###########################################################################

    ###########################################################################
    def __validate_type(self, type):
        types = ['all', 'cpu', 'gpu']
        type = type.strip().lower()
        if(type not in types):
            raise Exception(
                "Invalid work unit type! Must be %s" % (str(types)))
        return type
    ###########################################################################

    ###########################################################################
    def add_slot(self, type):
        type = self.__validate_type(type)
        if(self.__get_type_count(type) > 0):
            self.send('slot-add %s' % type)
        return self.get_slots()
    ###########################################################################

    ###########################################################################
    def get_client_info(self, category=None, key=None):
        data = {}
        if(category is None or key is None):
            info = self.send('info')
            for info_category in info:
                data[info_category[0]] = {}
                for category_key in info_category:
                    if(isinstance(category_key, list)):
                        data[info_category[0]][category_key[0]] = (
                            category_key[1])
        else:
            data = self.send('get-info %s %s' % (category, key))
        return data
    ###########################################################################

    ###########################################################################
    def get_cpu_count(self):
        return self.__get_type_count('cpu')
    ###########################################################################

    ###########################################################################
    def get_gpu_count(self):
        return self.__get_type_count('gpu')
    ###########################################################################

    ###########################################################################
    def get_options(self, name=None):
        data = {}
        if(name is None):
            data = self.send('options')
        else:
            data = self.send('option %s' % name)
        return data
    ###########################################################################

    ###########################################################################
    def get_slots(self, type="all"):
        type = self.__validate_type(type)
        data = self.send('slot-info')
        if(type == "all"):
            return data
        #######################################################################
        slots = list()
        for slot in data:
            if(type in slot['description']):
                slots.append(slot)
        return slots
    ###########################################################################

    ###########################################################################
    def get_slot_by_id(self, slot_id):
        slots = self.get_slots()
        for slot in slots:
            if(slot['id'] == slot_id):
                return slot
        raise Exception("Could not find slot by ID: %s " % slot_id)
    ###########################################################################

    ###########################################################################
    def get_work_by_slot_id(self, slot_id):
        slot = self.get_slot_by_id(slot_id)
        wus = self.get_work_queue()
        work = list()
        for wu in wus:
            if(wu['slot'] == slot['id']):
                work.append(wu)
        return work
    ###########################################################################

    ###########################################################################
    def get_work_queue(self, type="all"):
        type = self.__validate_type(type)
        data = self.send('queue-info')
        for unit in data:
            unit['nextattempt'] = self.__parse_time(unit['nextattempt'])
        if(type == "all"):
            return data
        #######################################################################
        wus = list()
        slots = self.get_slots(type)
        for wu in data:
            for slot in slots:
                if(wu['slot'] == slot['id']):
                    wus.append(wu)
                    break
        return wus
    ###########################################################################

    ###########################################################################
    def send(self, message):
        full_msg = ("%s\n" % message)
        byte_msg = full_msg.encode('ASCII')
        if(self.__can_write()):
            self.csocket.sendall(byte_msg)
        else:
            print("ERROR - can't write?")
        #######################################################################
        return self.__read()
    ###########################################################################

    ###########################################################################
    def set_option(self, name, value):
        self.send('option %s %s' % (name, value))
        data = {}
        data[name] = self.send('option %s' % name)
        return data
    ###########################################################################

    ###########################################################################
    def remove_slot(self, slot_id):
        slot = self.get_slot_by_id(slot_id)
        self.send('slot-delete %s' % slot['id'])
        time.sleep(1)
        return self.get_slots()
    ###########################################################################
