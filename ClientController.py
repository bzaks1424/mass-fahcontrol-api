import socket
import select
###############################################################################


###############################################################################
class ClientController:

    ###########################################################################
    # Vars
    address = ""
    port = 0
    password = ""
    init_commands = []
    retries = 0
    csocket = None
    ###########################################################################

    ###########################################################################
    def __init__(self, address='localhost', port=36330, password=None):
        self.address = address
        self.port = int(port)
        self.password = password
        self.init_commands = []
        #######################################################################
        self.__open()
    ###########################################################################

    ###########################################################################
    def __del__(self):
        self.__close()
    ###########################################################################

    ###########################################################################
    def __close(self):
        # if(debug):
        #     print("Closing Socket Connection")
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
        self.read()
        # if(debug):
        #     print("Socket Connected")
        if(self.password):
            self.send('auth "%s"' % self.password)
    ###########################################################################

    ###########################################################################
    def __reset(self):
        # if(debug):
        #     print("Resetting Socket Connection")
        self.__close()
    ###########################################################################

    ###########################################################################
    def can_read(self):
        rlist, wlist, xlist = select.select([self.csocket], [], [], 0)
        return len(rlist) != 0
    ###########################################################################

    ###########################################################################
    def can_write(self):
        rlist, wlist, xlist = select.select([], [self.csocket], [], 0)
        return len(wlist) != 0
    ###########################################################################

    ###########################################################################
    def parse(self, message):
        start = message.find('\nPyON ')
        if(start == -1):
            return message.strip()[:-1]
        else:
            return self.parse_pyon(message[start:])
    ###########################################################################

    ###########################################################################
    def parse_pyon(self, message):
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
                try:
                    return eval(data, {}, {})
                except Exception as e:
                    print(
                        'ERROR parsing PyON message: %s: %s'
                        % (str(e), data.encode('string_escape')))
            else:
                raise Exception(
                    'Invalid PyON line: %s' % line.encode('string_escape'))
    ###########################################################################

    ###########################################################################
    def read(self):
        full_buff = bytearray()
        buffer_size = 4096
        while True:
            local_buff = self.csocket.recv(buffer_size)
            buff_length = len(local_buff)
            # if(debug):
            #     print("  Recieved %d bytes" % buff_length)
            if(buff_length > 0):
                full_buff.extend(local_buff)
            if(not self.can_read()):
                break
        full_str = self.parse(full_buff.decode('ASCII'))
        # if(debug):
        #     print("  %s" % str(full_str))
        return full_str
    ###########################################################################

    ###########################################################################
    def send(self, message):
        full_msg = ("%s\n" % message)
        byte_msg = full_msg.encode('ASCII')
        if(self.can_write()):
            # if(debug):
            #     print("Command %s" % message)
            self.csocket.sendall(byte_msg)
        else:
            print("ERROR - can't write?")
        #######################################################################
        return self.read()
    ###########################################################################
