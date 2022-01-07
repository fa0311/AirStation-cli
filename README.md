# AirStation-Cli(Beta)

ブラウザでしか制御ができないBUFFALO AirStationをCUIで操作するソフトウェア及びPythonAPI<br>

## Installation

```shell
pip install git+https://github.com/fa0311/AirStation-cli
pip install -r requirements.txt
```

## Usage-Cli
### Description

```shell
# Python
python AirStationCli [OPTIONS] [ACTION]
```

#### Action
- Login
- GetName
- NatRegulation
- DhcpLeases

#### Options

| argument          | alias    | default      | choice            | type |
|-------------------|----------|--------------|-------------------|------|
| --default-gateway |          | 192.168.11.1 |                   |      |
| --username        | -u -user | admin        |                   |      |
| --password        | -p -pass | password     |                   |      |
| --login-mode      |          | auto         | auto, force, skip |      |
| --mobile          |          | false        |                   |      |
| --format          | -f       | table        | table, json, csv  |      |
| --output          | -o       | None         | file path         |      |
| --json-indent     |          | None         |                   | int  |

### Login

```shell
python AirStationCli nothing --default-gateway 192.168.11.1 -u admin -p password
# ログインに成功しました。 or パスワードが間違っています。etc.
```

### GetName

```shell
python AirStationCli name
# WSR-1166DHPL2 - BUFFALO AirStation
```

### NatRegulation

```shell
python AirStationCli nat-reg
# table
```
![screenshots](./docs/asset/img/nat_reg.png)

### DhcpLeases

```shell
python AirStationCli dhcp-leases
# table
```
![screenshots](./docs/asset/img/dhcp-leases.png)

## Usage-API

### AirStationCli.AirStationCli

```python
from AirStationCli import AirStationAPI
airstation = AirStationAPI.AirStationAPI(default_gateway="192.168.11.1")
```

| argument        | default      |
|-----------------|--------------|
| default_gateway | 192.168.11.1 |

### Login

```python
airstation.login_get().login_post(username="admin", password="password", mobile=False)
print(airstation.get_red_info())
# False or パスワードが間違っています。etc.
```

| argument        | default      |
|-----------------|--------------|
| username        | admin        |
| password        | password     |
| mobile          | false        |


### GetName

```python
print(airstation.index_adv().get_title())
# WSR-1166DHPL2 - BUFFALO AirStation
```

### Init

```python
airstation.init()
```

Attributes
- AirStationAPI: object
Methods
- downloadcfg(): str
- uploadcfg(cfgfile): str
- reboot(): bool

Note: `uploadcfg()` NotWorking

### NatRegulation

```python
airstation.nat_reg()
```

Attributes
- AirStationAPI: object
- data: List[AirStationAPINatData Object]

Methods
- add(group, lanip, wan="wan", nosave_proto="tcp/udp", porttype="tcp", wanport=80, lanport=80, ip="1.1.1.1"): bool

#### method add()

| argument     | default    | type                     | condition                                                                     |
|--------------|------------|--------------------------|-------------------------------------------------------------------------------|
| group        | (required) | str                      |                                                                               |
| lanip        | (required) | str                      |                                                                               |
| wan          | wan        | wan, manual              |                                                                               |
| nosave_proto | tcp/udp    | all, icmp, one, tcp/udp  |                                                                               |
| porttype     | tcp        | tcp, udp, ftp, etc.      | nosave_proto=tcp/udp                                                          |
| wanport      | 80         | int                      | nosave_proto=one or (nosave_proto=tcp/udp and (porttype=tcp or porttype=udp)) |
| lanport      | 80         | int                      | nosave_proto=tcp/udp and (porttype=tcp or porttype=udp)                       |
| ip           | 1.1.1.1    | str                      | wan=manual                                                                    |

```python
airstation.nat_reg().add(group="test", lanip="192.168.11.30", nosave_proto="tcp/udp", porttype="tcp", wanport=80, lanport=80)
```

#### @dataclass AirStationAPINatData
Attributes
- AirStationAPI: object
- id_name: str
- id_wan: str
- id_lanip: str
- id_proto: str
- id_wport: str
- id_lport: str
- id: str

Methods
- delete(): bool

### DhcpsLease

```python
airstation.dhcp_leases()
```

Attributes
- AirStationAPI: object
- data: List[AirStationAPIDHCPData Object]

Methods
- add(dhcp_ip, dhcp_mac): bool

```python
airstation.dhcp_leases().add("192.168.11.30","00:00:5e:00:53:00")
```

#### @dataclass AirStationAPIDHCPData
Attributes
- AirStationAPI: object
- DHCPLANIP: str
- DHCPLMAC: str
- LeasePeriod: str
- DHCPLease: str
- id: str

Methods
- delete(): bool
