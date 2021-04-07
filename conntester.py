import configparser

from ping3 import ping as p3p


class ConnTester():
    config = configparser.ConfigParser()
    hosts = []
    ping_timeout = 1

    def __init__(self):
        self.config.read('conntester.ini')
        self.hosts = self.config.get('MAIN', 'hosts').split(', ')
        self.ping_timeout = int(self.config.get('MAIN', 'timeout'))
    
    def ping(self, host):
        """
        Pings specified host and returns ping time in ms
        """
        return p3p(host, timeout=self.ping_timeout, unit='ms')
    
    def ping_all(self):
        """
        Pings all hosts from config
        """
        for host in self.hosts:
            print(f"Ping to {host} is {self.ping(host)}")

if __name__ == '__main__':
    ct = ConnTester()
    ct.ping_all()