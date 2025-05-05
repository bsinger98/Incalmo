from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser

import xml.etree.ElementTree as ET


class Parser(BaseParser):

    def parse(self, blob):
        try:
            # Parse XML blob
            root = ET.fromstring(blob)

            relationship = self.parse_xml_report(root)
            return relationship
        except Exception as e:
            print('exception when parsing nmap results xml: %s' % repr(e))
            return None

    def parse_xml_report(self, root):
        edge = "has_online_ipaddrs"
        online_ips = []
        subnet_fact = None

        try:
            nmapargs = root.get("args")
            subnet = nmapargs.split(" ")[-1]
        except:
            print("No subnet found in nmap args")
            return None

        # get all ips returned by nmap
        for host in root.findall('host'):
            host_ip = host.find('address').get('addr')       
            online_ips.append(host_ip)
        subnet_fact = Fact('host.subnet.ipaddrs', subnet)
        subnet_onlineips_fact = Fact('host.subnet.online_ipaddrs', online_ips)
        relationship = Relationship(source=subnet_fact, edge=edge, target=subnet_onlineips_fact)
        

        return [relationship]