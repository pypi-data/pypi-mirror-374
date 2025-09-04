# Functions from PyTango (test_context.py), added there in version 9.4.
# Copied here for backwards compatibility. Only used by test fixtures.

import socket
import time

import psutil


def get_server_port_via_pid(pid, host, retries=400, delay=0.03):
    """Return the TCP port that a device server process is listening on (GIOP).

    This checks TCP sockets open on the process with the given PID, and attempts
    to find the one that accepts GIOP traffic.  A connection will be made to each
    listening socket, and data may be sent to them.

    General Inter-ORB Protocol (GIOP) is the message protocol which object
    request brokers (ORBs) communicate in CORBA.  This port is the one that is
    used when connecting a DeviceProxy.  These are not the port(s) used for ZMQ
    event traffic.

    :param pid: operating system process identifier
    :type pid: int
    :param host: hostname/IP that device server is listening on.  E.g., 127.0.0.1,
    IP address of a non-loopback network interface, etc.  Note that starting a device
    server on "localhost" may fail if OmniORB creates an IPv6-only socket.
    :type pid: str
    :param retries: number of times to retry attempts, optional
    :type retries: int
    :param delay: time to wait (seconds) between retries, optional
    :type delay: float

    :returns: TCP port number
    :rtype: int

    :raises RuntimeError: If the GIOP port couldn't be identified

    .. versionadded:: 9.4.0
    .. versionadded:: 9.5.0
        *retries* parameter.
        *delay* parameter.
    """

    count = 0
    port = None
    last_err = None
    while port is None and count < retries:
        ports = _get_listening_tcp_ports(pid)
        try:
            port = _get_giop_port(host, ports)
        except Exception as err:
            last_err = err
            time.sleep(delay)
        count += 1

    if port is None:
        raise RuntimeError(
            f"Failed to get GIOP TCP port within {count * delay:.1f} sec"
        ) from last_err

    return port


def _get_listening_tcp_ports(pid):
    p = psutil.Process(pid)
    if hasattr(p, "net_connections"):
        conns = p.net_connections(kind="tcp")
    else:
        conns = p.connections(kind="tcp")  # deprecated in psutil v6.0.0
    return list(set([c.laddr.port for c in conns if c.status == "LISTEN"]))


def _get_giop_port(host, ports):
    protocols = _try_get_protocols_on_ports(host, ports)
    for port, protocol in protocols.items():
        if protocol == "GIOP":
            return port
    raise RuntimeError(
        f"None of ports {ports} appear to have GIOP protocol. "
        f"Guessed protocols: {protocols}."
    )


def _try_get_protocols_on_ports(host, ports):
    """Return a dict with port to protocol mapping.

    This attempts to establish a TCP socket connection to the host
    for each port, and then determine the protocol it supports.

    ZMQ client sockets receive an unsolicited version check message on connection.
    CORBA GIOP client sockets don't receive an unsolicited message, so we send
    a requested to disconnect, and expect an empty message back.
    """
    zmq_response = (
        b"\xff\x00\x00\x00\x00\x00\x00\x00\x01\x7f"  # signature + version check
    )
    giop_send = b"GIOP\x01\x02\x01\x05\x00\x00\x00\x00"  # request disconnect
    giop_response = b""  # graceful disconnect
    max_bytes_expected = len(zmq_response)

    protocols = dict.fromkeys(ports, "Unknown")
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(0.001)
            server_address = (host, port)
            sock.connect(server_address)

            try:
                data = sock.recv(max_bytes_expected)
                if data == zmq_response:
                    protocols[port] = "ZMQ"
                    continue
            except OSError:
                pass

            try:
                sock.sendall(giop_send)
                data = sock.recv(max_bytes_expected)
                if data == giop_response:
                    protocols[port] = "GIOP"
                    continue
            except OSError:
                pass
        except OSError:
            pass
        finally:
            sock.close()
    return protocols
