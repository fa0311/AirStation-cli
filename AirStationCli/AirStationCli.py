import AirStationAPI, AirStationTable
import argparse
import csv
from dataclasses import asdict, astuple
import pandas as pd

if __name__ == "__main__":

    # コマンドライン引数
    argpar = argparse.ArgumentParser(
        prog="AirStationCli",
        usage="https://github.com/fa0311/AirStation-cli",
        description="BUFFALO AirStation Command Line Interface",
    )
    argpar.add_argument("action")
    argpar.add_argument("-u", "-user", "--username", default="admin")
    argpar.add_argument("-p", "-pass", "--password", default="password")
    argpar.add_argument("--default-gateway", default="192.168.11.1")

    argpar.add_argument(
        "-f", "--format", default="table", choices=["table", "csv", "json"]
    )
    argpar.add_argument(
        "--login-mode", default="auto", choices=["auto", "force", "skip"]
    )

    argpar.add_argument("--mobile", action="store_true")

    arg = argpar.parse_args()

    # インスタンスの初期化
    airstation = AirStationAPI.AirStationCli(default_gateway=arg.default_gateway)

    # ログイン
    if arg.login_mode == "auto":
        if airstation.index_adv().get_title() == "Redirect Page":
            arg.login_mode = "force"
    if arg.login_mode == "force":
        info = (
            airstation.login_get()
            .login_post(arg.username, arg.password, mobile=arg.mobile)
            .get_red_info()
        )
        if info:
            exit(info)

    # アクション
    if arg.action == "name":
        data = airstation.login_get().get_title()

    elif arg.action == "nat-reg":
        data = airstation.nat_reg().data

    elif arg.action == "dhcp-leases":
        data = airstation.nat_reg().data

    # フォーマット
    if type(data) is str:
        print(data)
    elif type(data) is list:
        if arg.format in ["table", "csv"]:
            table = [tuple(asdict(data[0]).keys())[1:]]
            for row in data:
                table.append(astuple(row)[1:])
        if arg.format == "table":
            df = pd.DataFrame(table[1:], columns=table[0])
            pd.set_option('display.unicode.east_asian_width', True)
            print(df)
        elif arg.format == "csv":
            df = pd.DataFrame(table[1:], columns=table[0])
            print(df.to_csv())