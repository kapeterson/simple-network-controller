from netmiko import Netmiko


def get_device_driver(host_name=None, username=None, psswd=None, device_type=None):


    net_connect = Netmiko(host=host_name,
                          username=username,
                          password=psswd,
                          device_type=device_type)

    return net_connect