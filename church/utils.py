# church/utils.py
import requests

def getoauth():
    CLIENTID = "1000.WQBQ6R0UJD0M6ZSOVXP7IC9CER5IQS"
    CLIENTSECRET = "534c7f9055ce4897a66fa79cac68a5045325c5062c"
    REFRESHTOKEN = "1000.09c39c850b38bb7db691af070c898d0d.16915e29e13f7f67b72736ac0ce51a78"
    url = f"https://accounts.zoho.in/oauth/v2/token?client_id={CLIENTID}&grant_type=refresh_token&client_secret={CLIENTSECRET}&refresh_token={REFRESHTOKEN}"
    response = requests.post(url)
    data = response.json()
    return data.get("access_token")