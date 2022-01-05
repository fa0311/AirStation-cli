import AirStationAPI
import argparse


if __name__ == "__main__":
    argpar = argparse.ArgumentParser(
        prog="AirStationCli",
        usage="https://github.com/fa0311/AirStation-cli",
        description="BUFFALO AirStation Command Line Interface",
    )
    argpar.add_argument("action")
    argpar.add_argument("-u", "-user", "--username", default="admin")
    argpar.add_argument("-p", "-pass", "--password", default="password")
    argpar.add_argument("--default-gateway", default="192.168.11.1")

    argpar.add_argument("--login-skip", action="store_true")
    argpar.add_argument("--json", action="store_true")
    argpar.add_argument("--mobile", action="store_true")

    arg = argpar.parse_args()

    airstation = AirStationAPI.AirStationCli(default_gateway=arg.default_gateway)
    if not arg.login_skip:
        info = (
            airstation.login_get()
            .login_post(arg.username, arg.password, mobile=arg.mobile)
            .get_red_info()
        )
        print(info if info else "ログインに成功しました。")

    if arg.action == "name":
        print(airstation.index_adv().get_title())
