from struct import *

MSG_GET_RMS = 0
MSG_RMS_PACKET = 1
MSG_GET_DEVICES = 2
MSG_SET_FLOAT_PARAM = 3
MSG_LIST_DEVICES = 4
MSG_DB_PACKET = 5
MSG_SET_BOOLEAN_PARAM = 6
MSG_CONFIGUREDB = 7

class MsgBase(object):
    def __init__(self):
        self.data = bytearray()

    def serialize(self) -> bytearray:
        return pack('<I', len(self.data)) + self.data

    def deserialize(data : bytearray) -> object:
        return None

    def deserializeInto(self):
        return None

    def add_int16(self, value):
        self.data += pack('<h', value)

    def add_int32(self, value):
        self.data += pack('<i', value)

    def add_float32(self, value):
        self.data += pack('<f', value)

    def add_string(self, value):
        if isinstance(value, str):
            value = value.encode()

        assert len(value) <= 65535

        self.data += pack('<H', len(value))
        self.data += value

    def pop_length(self):
        value = unpack('<I', self.data[:calcsize('<I')])
        self.data = self.data[calcsize('<I'):]
        return value[0]

    def pop_int16(self):
        value = unpack('<h', self.data[:calcsize('<h')])
        self.data = self.data[calcsize('<h'):]
        return value[0]

    def pop_int32(self):
        value = unpack('<i', self.data[:calcsize('<i')])
        self.data = self.data[calcsize('<i'):]
        return value[0]

    def pop_float32(self):
        value = unpack('<f', self.data[:calcsize('<f')])
        self.data = self.data[calcsize('<f'):]
        return value[0]

    def pop_string(self) -> str:
        str_length = unpack('<H', self.data[:calcsize('<H')])[0]
        self.data = self.data[calcsize('<H'):]

        string = self.data[:str_length].decode()
        self.data = self.data[str_length:]

        return string

class MsgGetDevices(MsgBase):
    def __init__(self):
        super().__init__()

        self.type = MSG_GET_DEVICES

    def serialize(self) -> bytearray:
        
        self.add_int32(self.type)
        return pack('<I', len(self.data) + calcsize('<I')) + self.data

    def deserialize(_data : bytearray) -> object:
        return

class MsgDeviceList(MsgBase):
    def __init__(self):
        super().__init__()

        self.type = MSG_LIST_DEVICES
        self.devices = {}

    def serialize(self) -> bytearray:
        self.add_int32(self.type)
        self.add_int32(len(self.devices))
        for device_id, device_name_ch in self.devices.items():
            self.add_int32(device_id)
            self.add_string(device_name_ch[0])
            self.add_int32(device_name_ch[1])

        return pack('<I', len(self.data) + calcsize('<I')) + self.data

    def deserialize(_data: bytearray) -> object:
        msg = MsgDeviceList()

        msg.data = _data
        msg_length = msg.pop_length()
        msg_type = msg.pop_int32()
        
        device_count = msg.pop_int32()

        for i in range(0, device_count):
            device_id = msg.pop_int32()
            print("Got device ID: ", device_id)
            device_name = msg.pop_string()
            device_channels = msg.pop_int32()
            msg.devices[str(device_id)] = (device_name, device_channels)
            print("Got device name: ", device_name)

        return msg


class MsgRMSPacket(MsgBase):
    def __init__(self):
        super().__init__()

        self.type = MSG_RMS_PACKET
        self.value = 0.0

    def serialize(self) -> bytearray:
        self.add_int32(self.type)
        self.add_float32(self.value)
        return pack('<I', len(self.data) + calcsize('<I')) + self.data

    def deserialize(_data : bytearray) -> object:
        msg = MsgRMSPacket()

        msg.data = _data
        msg_length = msg.pop_length()
        msg_type = msg.pop_int32()
        msg.value = msg.pop_float32()

        return msg

c_id = 0
class MsgdBPacket(MsgBase):
    def __init__(self):
        super().__init__()

        self.type = MSG_DB_PACKET
        self.value = 0.0
        self.id = c_id
        global c_id
        c_id += 1

    def serialize(self) -> bytearray:
        self.add_int32(self.type)
        self.add_float32(self.value)
        self.add_int32(self.id)
        return pack('<I', len(self.data) + calcsize('<I')) + self.data

    def deserialize(_data : bytearray) -> object:
        msg = MsgdBPacket()

        msg.data = _data
        msg_length = msg.pop_length()
        msg_type = msg.pop_int32()
        msg.value = msg.pop_float32()
        return msg

class MsgStartStreamingRMS(MsgBase):
    def __init__(self):
        super().__init__()

        self.type = MSG_GET_RMS
        self.devices = []
        self.channels = []

    def serialize(self) -> bytearray:
        self.add_int32(self.type)
        self.add_int32(len(self.devices))
        for device in self.devices:
            self.add_int32(device)

        for device_channels in self.channels:
            self.add_int32(len(device_channels))
            for channel in device_channels:
                self.add_int32(channel)

        return pack('<I', len(self.data) + calcsize('<I')) + self.data

    def deserialize(_data : bytearray) -> object:
        msg = MsgStartStreamingRMS()

        msg.data = _data
        msg_length = msg.pop_length()
        msg_type = msg.pop_int32()

        device_count = msg.pop_int32()
        for i in range(0, device_count):
            msg.devices.append(msg.pop_int32())

        for i in range(0, device_count):
            channel_count = msg.pop_int32()
            channels_for_device = []
            for j in range(0, channel_count):
                channels_for_device.append(msg.pop_int32())

            msg.channels.append(channels_for_device)

        #msg.device = msg.pop_int32()
        #msg.channel = msg.pop_int32()

        return msg

class MsgSetFloatParam(MsgBase):
    def __init__(self):
        super().__init__()

        self.type = MSG_SET_FLOAT_PARAM
        self.param_name = "none"
        self.param_value = 1.0

    def serialize(self) -> bytearray:
        self.add_int32(self.type)
        self.add_string(self.param_name)
        self.add_float32(self.param_value)
        return pack('<I', len(self.data) + calcsize('<I')) + self.data

    def deserialize(_data : bytearray) -> object:
        msg = MsgSetFloatParam()

        msg.data = _data
        msg_length = msg.pop_length()
        msg_type = msg.pop_int32()
        msg.param_name = msg.pop_string()
        msg.param_value = msg.pop_float32()
        return msg

class MsgSetBooleanParam(MsgBase):
    def __init__(self):
        super().__init__()

        self.type = MSG_SET_BOOLEAN_PARAM
        self.param_name = "none"
        self.param_value = True

    def serialize(self) -> bytearray:
        self.add_int32(self.type)
        self.add_string(self.param_name)
        self.add_int16(int(self.param_value))
        return pack('<I', len(self.data) + calcsize('<I')) + self.data

    def deserialize(_data : bytearray) -> object:
        msg = MsgSetBooleanParam()

        msg.data = _data
        msg_length = msg.pop_length()
        msg_type = msg.pop_int32()
        msg.param_name = msg.pop_string()
        msg.param_value = bool(msg.pop_int16())
        return msg

class MsgConfiguredB(MsgBase):
    def __init__(self):
        super().__init__()

        self.type = MSG_CONFIGUREDB
        self.target_db = 0.0

    def serialize(self) -> bytearray:
        self.add_int32(self.type)
        self.add_float32(self.target_db)
        return pack('<I', len(self.data) + calcsize('<I')) + self.data

    def deserialize(_data : bytearray) -> object:
        msg = MsgConfiguredB()

        msg.data = _data
        msg_length = msg.pop_length()
        msg_type = msg.pop_int32()
        msg.target_db = msg.pop_float32()
        return msg