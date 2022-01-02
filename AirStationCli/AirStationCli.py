import requests
import re
from dataclasses import dataclass
import datetime


class AirStationCli:
    def __init__(self):
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        self.session = requests.session()
        self.BASE_URL = "http://192.168.11.1/"

    def get_session(self):
        reg = r'<input type="hidden" name="nosave_session_num" value="(\d+)">'
        return int(re.findall(reg, self.response.text)[0])

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT 0900 (日本標準時)")

    def login_get(self):
        self.response = self.session.get(self.BASE_URL + "login.html")
        return self

    def login_post(self, username, password):
        data = {
            "nosave_Username": username,
            "nosave_Password": password,
            "MobileDevice": 0,
            "nosave_session_num": self.get_session(),
        }
        self.response = self.session.post(self.BASE_URL + "login.html", data=data)
        return self

    def index_adv(self):
        self.response = self.session.get(self.BASE_URL + "index_adv.html")
        return self

    # dhcps_lease.html 構文ミスがひどい...
    def dhcps_lease(self):
        self.response = self.session.get(self.BASE_URL + "dhcps_lease.html")
        data = {
            "name": "(DHCPLANIP|DHCPLMAC|LeasePeriod|DHCPLease|id_BtuStatus)",
            "any": "(.+)",
            "number": "(\\d+)",
        }
        reg = '<td><div name="{name}{number}">{any}</div></td>'.format(**data)
        return AirStationCliDHCP(
            AirStationCli=self,
            data=re.findall(reg, self.response.content.decode("utf-8")),
        )

    def route_reg(self):
        self.response = self.session.get(self.BASE_URL + "route_reg.html")
        return self


@dataclass
class AirStationCliDHCP:
    AirStationCli: object = None
    data: list = None

    def __post_init__(self):
        self.data = [
            AirStationCliDHCPData(
                AirStationCli=self.AirStationCli,
                **{
                    self.data[i * 4 + ii][0]: self.data[i * 4 + ii][2]
                    for ii in range(4)
                },
                Id=self.data[i * 4][1]
            )
            for i in range(int(len(self.data) / 4))
        ]

    def add(self, dhcp_ip, dhcp_mac):
        data = {
            "nosave_dhcp_ip": dhcp_ip,
            "nosave_dhcp_mac": dhcp_mac,
            "nosave_session_num": self.AirStationCli.get_session(),
        }
        params = {"timestampt": self.AirStationCli.get_timestamp()}
        self.response = self.AirStationCli.session.post(
            self.AirStationCli.BASE_URL + "dhcps_lease.html", params=params, data=data
        )
        return "設定が完了しました。再スタートしています。" in self.response.content.decode("utf-8")


@dataclass
class AirStationCliDHCPData:
    AirStationCli: object = None
    DHCPLANIP: str = None
    DHCPLMAC: str = None
    LeasePeriod: str = None
    DHCPLease: str = None
    Id: str = None

    def delete(self):
        data = {
            "nosave_DDelete": int(self.Id),
            "nosave_session_num": self.AirStationCli.get_session(),
        }
        params = {"timestampt": self.AirStationCli.get_timestamp()}
        self.response = self.AirStationCli.session.post(
            self.AirStationCli.BASE_URL + "dhcps_lease.html", params=params, data=data
        )
        return "設定が完了しました。再スタートしています。" in self.response.content.decode("utf-8")
