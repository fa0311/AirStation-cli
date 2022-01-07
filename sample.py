from AirStationCli import AirStationAPI
import time


def save(response):
    with open("save.html", "w", encoding="utf-8") as f:
        f.write(response.text)

print(
    AirStationAPI.AirStationAPI()
    .login_get()
    .login_post(username="admin", password="m3ckv7dy")
    .nat_reg().data
)

exit()

print(
    AirStationAPI.AirStationAPI()
    .login_get()
    .login_post(username="admin", password="m3ckv7dy")
    .nat_reg()
    .add(
        group="aaaaa",
        lanip="192.168.11.20",
        nosave_proto="tcp/udp",
        porttype="tcp",
        wanport=25565,
        lanport=25565,
    )
)


print(
    AirStationAPI.AirStationAPI()
    .login_get()
    .login_post("admin", "m3ckv7dy")
    .nat_reg()
    .add("gwa", "192.168.11.25", wanport=254, lanport=485)
)


print(
    AirStationAPI.AirStationAPI()
    .login_get()
    .login_post("admin", "m3ckv7dy")
    .init()
    .reboot()
)

print(
    AirStationAPI.AirStationAPI()
    .login_get()
    .login_post("admin", "m3ckv7dy")
    .dhcp_leases()
)

# 名前一致したら消すやつ
while True:
    dhcps = (
        AirStationAPI.AirStationAPI()
        .login_get()
        .login_post("admin", "m3ckv7dy")
        .dhcp_leases()
        .add("aaaa", "aaaaa")
        .content
    )
    for data in dhcps.data:
        if data.DHCPLMAC == "YYYYY":
            data.delete()
            time.sleep(10)
            break
    else:
        break


def pass_gen(value):
    if int(value / 36):
        return (
            pass_gen(int(value / 36))
            + ([str(i) for i in range(10)] + [chr(i) for i in range(97, 123)])[
                value % 36
            ]
        )
    return ([str(i) for i in range(10)] + [chr(i) for i in range(97, 123)])[value % 36]
