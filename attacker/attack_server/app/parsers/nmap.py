from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser

import xml.etree.ElementTree as ET


class Parser(BaseParser):

    def parse(self, blob):
        try:
            # Parse XML blob
            root = ET.fromstring(blob)
            relationships = []

            for mp in self.mappers:
                try:
                    for host in root.findall("host"):
                        # call function based on target value
                        match = self.parse_options[mp.target.split('.').pop()](host)
                        if match:
                            host_ip = self.parse_host_ip(host)
                            relationships.append(Relationship(source=Fact(mp.source, host_ip),
                                                              edge=mp.edge,
                                                              target=Fact(mp.target, match)))
                except Exception as e:
                    print('Problem with mapper: %s - %s ' % (mp, e))
            return relationships
        except Exception as e:
            print('exception when parsing nmap results xml: %s' % repr(e))
            return None

    @property
    def parse_options(self):
        return dict(
            host_ip = self.parse_host_ip,
            hostname=self.parse_hostname,
            ports=self.parse_ports,
            services=self.parse_services,
            port_services=self.parse_port_services,
        )
    
    @staticmethod
    def parse_host_ip(host):
        return host.find('address').get('addr')

    @staticmethod
    def parse_hostname(host):
        return host.find('hostnames/hostname').get('name')
    
    @staticmethod
    def parse_ports(host):
        ports = []
        for port in host.findall('ports/port'):
            ports.append(port.get('portid'))
        return ports
    
    @staticmethod
    def parse_services(host):
        services = []
        for port in host.findall('ports/port'):
            services.append(port.find('service').get('name'))
        return services
    
    @staticmethod
    def parse_port_services(host):
        port_services = []
        for port in host.findall('ports/port'):
            port_services.append((port.get('portid'), port.find('service').get('name')))
        return port_services
