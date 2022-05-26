import AirStationCli.AirStationAPI

airstation = AirStationCli.AirStationAPI.AirStationAPI(default_gateway="192.168.11.1")
airstation.login_get().login_post("admin", "password").get_red_info()
airstation.nat_reg().add(group="rustdesk", lanip="192.168.11.20", nosave_proto="tcp/udp", porttype="tcp", wanport=21115, lanport=21115)