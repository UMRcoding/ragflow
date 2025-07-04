
import requests
import urllib.parse


class UserInfo:
    def __init__(self, email, username, nickname, avatar_url):
        self.email = email
        self.username = username
        self.nickname = nickname
        self.avatar_url = avatar_url
    
    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()}


class OAuthClient:
    def __init__(self, config):
        """
        Initialize the OAuthClient with the provider's configuration.
        """
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.authorization_url = config["authorization_url"]
        self.token_url = config["token_url"]
        self.userinfo_url = config["userinfo_url"]
        self.redirect_uri = config["redirect_uri"]
        self.scope = config.get("scope", None)

        self.http_request_timeout = 7


    def get_authorization_url(self, state=None):
        """
        Generate the authorization URL for user login.
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        if self.scope:
            params["scope"] = self.scope
        if state:
            params["state"] = state
        authorization_url = f"{self.authorization_url}?{urllib.parse.urlencode(params)}"
        return authorization_url


    def exchange_code_for_token(self, code):
        """
        Exchange authorization code for access token.
        """
        try:
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            response = requests.post(
                self.token_url,
                data=payload,
                headers={"Accept": "application/json"},
                timeout=self.http_request_timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to exchange authorization code for token: {e}")


    def fetch_user_info(self, access_token, **kwargs):
        """
        Fetch user information using access token.
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(self.userinfo_url, headers=headers, timeout=self.http_request_timeout)
            response.raise_for_status()
            user_info = response.json()
            return self.normalize_user_info(user_info)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch user info: {e}")


    def normalize_user_info(self, user_info):
        email = user_info.get("email")
        username = user_info.get("username", str(email).split("@")[0])
        nickname = user_info.get("nickname", username)
        avatar_url = user_info.get("avatar_url", None)
        if avatar_url is None:
            avatar_url = user_info.get("picture", "")
        return UserInfo(email=email, username=username, nickname=nickname, avatar_url=avatar_url)
