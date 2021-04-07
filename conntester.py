from ping3 import ping as p3p


def ping(host):
    """
    Pings specified host and returns ping time in ms
    """
    return p3p(host, unit='ms')


if __name__ == '__main__':
    hosts = {
        'google': 'google.com',
        'google_dns': '8.8.8.8',
        'nonexistent': '192.168.2.2'
    }
    for name, host in hosts.items():
        print(f"Ping to {name} is {ping(host)}")
