
import requests
from .oauth import OAuthClient, UserInfo


class GithubOAuthClient(OAuthClient):
    def __init__(self, config):
        """
        Initialize the GithubOAuthClient with the provider's configuration.
        """
        config.update({
            "authorization_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scope": "user:email"
        })
        super().__init__(config)


    def fetch_user_info(self, access_token, **kwargs):
        """
        Fetch github user info.
        """
        user_info = {}
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            # user info
            response = requests.get(self.userinfo_url, headers=headers, timeout=self.http_request_timeout)
            response.raise_for_status()
            user_info.update(response.json())
            # email info
            response = requests.get(self.userinfo_url+"/emails", headers=headers, timeout=self.http_request_timeout)
            response.raise_for_status()
            email_info = response.json()
            user_info["email"] = next(
                (email for email in email_info if email["primary"]), None
            )["email"]
            return self.normalize_user_info(user_info)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch github user info: {e}")


    def normalize_user_info(self, user_info):
        email = user_info.get("email")
        username = user_info.get("login", str(email).split("@")[0])
        nickname = user_info.get("name", username)
        avatar_url = user_info.get("avatar_url", "")
        return UserInfo(email=email, username=username, nickname=nickname, avatar_url=avatar_url)
