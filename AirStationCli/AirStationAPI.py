import requests
import re
from dataclasses import dataclass
import datetime
import html


class AirStationAPI:
    def __init__(self, default_gateway="192.168.11.1"):
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        self.session = requests.session()
        self.BASE_URL = "http://{0}/".format(default_gateway)

    def get_red_info(self):
        reg = r'<div style="color:red">(.*?)</div>'
        find = re.findall(reg, self.content)
        return False if len(find) == 0 else find[0]

    def get_title(self):
        reg = r"<title>(.*?)</title>"
        find = re.findall(reg, self.content)
        return False if len(find) == 0 else find[0]

    def is_redirect_page(self):
        return self.get_title() == "Redirect Page"

    def is_wait(self):
        return self.get_title() == "しばらくお待ちください。"

    def re_format(self, content):
        return html.unescape(content.decode("utf-8"))

    def get_session(self):
        reg = r'<input type="hidden" name="nosave_session_num" value="(\d+)">'
        return int(re.findall(reg, self.content)[0])

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT 0900 (日本標準時)")

    def login_get(self):
        self.content = self.re_format(
            self.session.get(self.BASE_URL + "login.html").content
        )
        return self

    def login_post(self, username, password, mobile=False):
        if mobile:
            data = {
                "nosave_Username": username,
                "nosave_Password": password,
                "MobileDevice": 0,
                "nosave_session_num": self.get_session(),
            }
        else:
            data = {
                "nosave_Username": username,
                "nosave_Password": password,
                "MobileDevice": 0,
                "mobile": "on",
                "nosave_session_num": self.get_session(),
            }
        self.content = self.re_format(
            self.session.post(self.BASE_URL + "login.html", data=data).content
        )
        return self

    def index_adv(self):
        self.content = self.re_format(
            self.session.get(self.BASE_URL + "index_adv.html").content
        )
        return self

    def init(self):
        self.content = self.re_format(
            self.session.get(self.BASE_URL + "init.html").content
        )
        return AirStationAPIInit(AirStationAPI=self)

    def route_reg(self):
        self.content = self.re_format(
            self.session.get(self.BASE_URL + "route_reg.html").content
        )
        return self

    def nat_reg(self):
        self.content = self.re_format(
            self.session.get(self.BASE_URL + "nat_reg.html").content
        )
        data = {
            "name": "(id_name|id_wan|id_lanip|id_proto|id_wport|id_lport)",
            "any": "(.*?)",
            "number": "(\\d+)",
        }
        reg = '<span id="{name}{number}">{any}</span>'.format(**data)
        return AirStationAPINat(
            AirStationAPI=self,
            data=re.findall(reg, self.content),
        )

    def dhcp_leases(self):
        self.content = self.re_format(
            self.session.get(self.BASE_URL + "dhcps_lease.html").content
        )
        data = {
            "name": "(DHCPLANIP|DHCPLMAC|LeasePeriod|DHCPLease|id_BtuStatus)",
            "any": "(.*?)",
            "number": "(\\d+)",
        }
        reg = '<td><div name="{name}{number}">{any}</div></td>'.format(**data)
        return AirStationAPIDHCP(
            AirStationAPI=self,
            data=re.findall(reg, self.content),
        )


class AirStationAPIInit:
    def __init__(self, AirStationAPI):
        self.AirStationAPI = AirStationAPI

    def downloadcfg(self):
        data = {
            "nosave_buttoncfg": 1,
            "nosave_saveConfRC4Key": "",
            "nosave_saveConfRC4Encryption": 0,
            "nosave_loadConfRC4Encryption": 0,
            "nosave_session_num": self.AirStationAPI.get_session(),
        }
        response = self.AirStationAPI.session.post(
            self.AirStationAPI.BASE_URL + "init.html", data=data
        )
        return response

    def uploadcfg(self, cfgfile):
        file = {"nosave_F14": cfgfile}
        self.AirStationAPI.content = self.re_format(
            self.AirStationAPI.session.post(
                self.AirStationAPI.BASE_URL + "init.html", files=file
            ).content
        )
        return self.AirStationAPI.is_wait()

    def reboot(self):
        data = {
            "nosave_reboot": 1,
            "nosave_session_num": self.AirStationAPI.get_session(),
        }
        self.AirStationAPI.content = self.re_format(
            self.AirStationAPI.session.post(
                self.AirStationAPI.BASE_URL + "init.html", data=data
            ).content
        )
        return self.AirStationAPI.is_wait()


@dataclass
class AirStationAPINat:
    AirStationAPI: object = None
    data: list = None

    def __post_init__(self):
        for i in range(int(self.data[-1][1])):
            if self.data[i * 6][0] != "id_name":
                self.data.insert(
                    i * 6, ("id_name", str(i + 1), self.data[i * 6 - 6][2])
                )

        self.data = [
            AirStationAPINatData(
                AirStationAPI=self.AirStationAPI,
                **{
                    self.data[i * 6 + ii][0]: self.data[i * 6 + ii][2]
                    for ii in range(6)
                },
                id=self.data[i * 6 + 1][1]
            )
            for i in range(int(len(self.data) / 6))
        ]

    def add(
        self,
        group,
        lanip,
        wan="wan",
        nosave_proto="tcp/udp",
        porttype="tcp",
        wanport=80,
        lanport=80,
        ip="1.1.1.1",
    ):
        data = {
            "nosave_wan": wan,
            "nosave_proto": nosave_proto,
            "nosave_lanip": lanip,
            "nosave_add": 1,
            "nosave_add_tmp": 0,
            "nosave_erritem": "",
            "nosave_errcontent": "",
            "nosave_session_num": self.AirStationAPI.get_session(),
        }
        for value in self.data:
            if value.id_name == group:
                data.update(
                    {
                        "nosave_grpList": -1,
                        "nosave_grpName": group,
                    }
                )
                break
        else:
            data.update(
                {
                    "nosave_grpList": group,
                }
            )

        if wan == "manual":
            data.update({"nosave_manualIP": ip})
        if nosave_proto == "one":
            data.update({"nosave_ProtNum": wanport})
        elif nosave_proto == "tcp/udp":
            data.update(
                {
                    "nosave_PortType": porttype,
                }
            )
            if porttype in ["tcp", "udp"]:
                data.update(
                    {
                        "nosave_wport": wanport,
                        "nosave_lport": lanport,
                    }
                )

        params = {"timestampt": self.AirStationAPI.get_timestamp()}
        self.AirStationAPI.content = self.AirStationAPI.re_format(
            self.AirStationAPI.session.post(
                self.AirStationAPI.BASE_URL + "nat_reg.html", params=params, data=data
            ).content
        )
        return self.AirStationAPI.is_wait()


@dataclass
class AirStationAPINatData:
    AirStationAPI: object = None
    id_name: str = None
    id_wan: str = None
    id_lanip: str = None
    id_proto: str = None
    id_wport: str = None
    id_lport: str = None
    id: str = None

    def delete(self):
        data = {
            "nosave_grpList": -1,
            "nosave_grpName": "",
            "nosave_wan": "wan",
            "nosave_proto": "tcp/udp",
            "nosave_PortType": "tcp",
            "nosave_wport": "",
            "nosave_lanip": self.id_lanip,
            "nosave_lport": "",
            "nosave_add_tmp": 0,
            "nosave_del": self.id,
            "nosave_erritem": "",
            "nosave_errcontent": "",
            "nosave_session_num": self.AirStationAPI.get_session(),
        }
        params = {"timestampt": self.AirStationAPI.get_timestamp()}
        self.AirStationAPI.content = self.AirStationAPI.re_format(
            self.AirStationAPI.session.post(
                self.AirStationAPI.BASE_URL + "nat_reg.html", params=params, data=data
            ).content
        )
        return self.AirStationAPI.is_wait()


@dataclass
class AirStationAPIDHCP:
    AirStationAPI: object = None
    data: list = None

    def __post_init__(self):
        self.data = [
            AirStationAPIDHCPData(
                AirStationAPI=self.AirStationAPI,
                **{
                    self.data[i * 4 + ii][0]: self.data[i * 4 + ii][2]
                    for ii in range(4)
                },
                id=self.data[i * 4 + 1][1]
            )
            for i in range(int(len(self.data) / 4))
        ]

    def add(self, dhcp_ip, dhcp_mac):
        data = {
            "nosave_dhcp_ip": dhcp_ip,
            "nosave_dhcp_mac": dhcp_mac,
            "nosave_session_num": self.AirStationAPI.get_session(),
        }
        params = {"timestampt": self.AirStationAPI.get_timestamp()}
        self.AirStationAPI.content = self.AirStationAPI.re_format(
            self.AirStationAPI.session.post(
                self.AirStationAPI.BASE_URL + "dhcps_lease.html",
                params=params,
                data=data,
            ).content
        )
        return self.AirStationAPI.is_wait()


@dataclass
class AirStationAPIDHCPData:
    AirStationAPI: object = None
    DHCPLANIP: str = None
    DHCPLMAC: str = None
    LeasePeriod: str = None
    DHCPLease: str = None
    id: str = None

    def delete(self):
        data = {
            "nosave_DDelete": int(self.id),
            "nosave_session_num": self.AirStationAPI.get_session(),
        }
        params = {"timestampt": self.AirStationAPI.get_timestamp()}
        self.AirStationAPI.content = self.AirStationAPI.re_format(
            self.AirStationAPI.session.post(
                self.AirStationAPI.BASE_URL + "dhcps_lease.html",
                params=params,
                data=data,
            ).content
        )
        return self.AirStationAPI.is_wait()
