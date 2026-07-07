# church/utils.py

import requests
from . import models
from django.utils import timezone
from datetime import timedelta


def IntiateOauth():

    expiry_time = timezone.now() - timedelta(minutes=50)
    oauth = models.Oauth.objects.filter(id=1).first()
    if oauth.modify_at < expiry_time:
        CLIENTID = "1000.WQBQ6R0UJD0M6ZSOVXP7IC9CER5IQS"
        CLIENTSECRET = "534c7f9055ce4897a66fa79cac68a5045325c5062c"
        REFRESHTOKEN = "1000.09c39c850b38bb7db691af070c898d0d.16915e29e13f7f67b72736ac0ce51a78"

        url = (
            "https://accounts.zoho.in/oauth/v2/token"
            f"?refresh_token={REFRESHTOKEN}"
            f"&client_id={CLIENTID}"
            f"&client_secret={CLIENTSECRET}"
            "&grant_type=refresh_token"
        )

        response = requests.post(url)
        data = response.json()
        oauth.refresh_token = data.get("access_token")
        oauth.save(update_fields=["refresh_token","modify_at"])
        print("new token")
        return data.get("access_token")
    else:
        print("Existed token")
        return  oauth.refresh_token

