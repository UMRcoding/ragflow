import json
import logging
import re
import secrets
from datetime import datetime

from flask import redirect, request, session
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from api import settings
from api.apps.auth import get_auth_client
from api.db import FileType, UserTenantRole
from api.db.db_models import TenantLLM
from api.db.services.file_service import FileService
from api.db.services.llm_service import LLMService, TenantLLMService
from api.db.services.user_service import TenantService, UserService, UserTenantService
from api.utils import (
    current_timestamp,
    datetime_format,
    decrypt,
    download_img,
    get_format_time,
    get_uuid,
)
from api.utils.api_utils import (
    construct_response,
    get_data_error_result,
    get_json_result,
    server_error_response,
    validate_request,
)

@manager.route("/login", methods=["POST", "GET"])  # noqa: F821
def login():
    if not request.json:
        return get_json_result(data=False, code=settings.RetCode.AUTHENTICATION_ERROR, message="未授权访问!")

    email = request.json.get("email", "")
    users = UserService.query(email=email)
    # 未注册用户返回错误
    if not users:
        return get_json_result(
            data=False,
            code=settings.RetCode.AUTHENTICATION_ERROR,
            message=f"邮箱 {email} 未注册！",
        )

    # 解密密码字段
    password = request.json.get("password")
    try:
        password = decrypt(password)
    except BaseException:
        return get_json_result(data=False, code=settings.RetCode.SERVER_ERROR, message="密码解密失败")

    # 校验邮箱 + 密码
    user = UserService.query_user(email, password)
    if user:
        # 登录成功
        response_data = user.to_json()
        user.access_token = get_uuid()
        login_user(user)
        user.update_time = (current_timestamp(),)
        user.update_date = (datetime_format(datetime.now()),)
        user.save()
        msg = "欢迎回来！"
        return construct_response(data=response_data, auth=user.get_id(), message=msg)
    else:
        return get_json_result(
            data=False,
            code=settings.RetCode.AUTHENTICATION_ERROR,
            message="邮箱和密码不匹配，请重新输入！",
        )


@manager.route("/login/channels", methods=["GET"])  # noqa: F821
def get_login_channels():
    """
    获取所有支持的登录方式（认证渠道）
    """
    try:
        channels = []
        for channel, config in settings.OAUTH_CONFIG.items():
            channels.append(
                {
                    "channel": channel,
                    "display_name": config.get("display_name", channel.title()),
                    "icon": config.get("icon", "sso"),
                }
            )
        return get_json_result(data=channels)
    except Exception as e:
        logging.exception(e)
        return get_json_result(data=[], message=f"Load channels failure, error: {str(e)}", code=settings.RetCode.EXCEPTION_ERROR)


@manager.route("/login/<channel>", methods=["GET"])  # noqa: F821
def oauth_login(channel):
    channel_config = settings.OAUTH_CONFIG.get(channel)
    if not channel_config:
        raise ValueError(f"Invalid channel name: {channel}")
    auth_cli = get_auth_client(channel_config)

    state = get_uuid()
    session["oauth_state"] = state
    auth_url = auth_cli.get_authorization_url(state)
    return redirect(auth_url)


@manager.route("/oauth/callback/<channel>", methods=["GET"])  # noqa: F821
def oauth_callback(channel):
    """
    Handle the OAuth/OIDC callback for various channels dynamically.
    """
    try:
        channel_config = settings.OAUTH_CONFIG.get(channel)
        if not channel_config:
            raise ValueError(f"Invalid channel name: {channel}")
        auth_cli = get_auth_client(channel_config)

        # Check the state
        state = request.args.get("state")
        if not state or state != session.get("oauth_state"):
            return redirect("/?error=invalid_state")
        session.pop("oauth_state", None)

        # Obtain the authorization code
        code = request.args.get("code")
        if not code:
            return redirect("/?error=missing_code")

        # Exchange authorization code for access token
        token_info = auth_cli.exchange_code_for_token(code)
        access_token = token_info.get("access_token")
        if not access_token:
            return redirect("/?error=token_failed")

        id_token = token_info.get("id_token")

        # Fetch user info
        user_info = auth_cli.fetch_user_info(access_token, id_token=id_token)
        if not user_info.email:
            return redirect("/?error=email_missing")

        # Login or register
        users = UserService.query(email=user_info.email)
        user_id = get_uuid()

        if not users:
            try:
                try:
                    avatar = download_img(user_info.avatar_url)
                except Exception as e:
                    logging.exception(e)
                    avatar = ""

                users = user_register(
                    user_id,
                    {
                        "access_token": get_uuid(),
                        "email": user_info.email,
                        "avatar": avatar,
                        "nickname": user_info.nickname,
                        "login_channel": channel,
                        "last_login_time": get_format_time(),
                        "is_superuser": False,
                    },
                )

                if not users:
                    raise Exception(f"Failed to register {user_info.email}")
                if len(users) > 1:
                    raise Exception(f"Same email: {user_info.email} exists!")

                # Try to log in
                user = users[0]
                login_user(user)
                return redirect(f"/?auth={user.get_id()}")

            except Exception as e:
                rollback_user_registration(user_id)
                logging.exception(e)
                return redirect(f"/?error={str(e)}")

        # User exists, try to log in
        user = users[0]
        user.access_token = get_uuid()
        login_user(user)
        user.save()
        return redirect(f"/?auth={user.get_id()}")
    except Exception as e:
        logging.exception(e)
        return redirect(f"/?error={str(e)}")


@manager.route("/github_callback", methods=["GET"])  # noqa: F821
def github_callback():
    """
    **Deprecated**, Use `/oauth/callback/<channel>` instead.

    GitHub OAuth callback endpoint.
    ---
    tags:
      - OAuth
    parameters:
      - in: query
        name: code
        type: string
        required: true
        description: Authorization code from GitHub.
    responses:
      200:
        description: Authentication successful.
        schema:
          type: object
    """
    import requests

    res = requests.post(
        settings.GITHUB_OAUTH.get("url"),
        data={
            "client_id": settings.GITHUB_OAUTH.get("client_id"),
            "client_secret": settings.GITHUB_OAUTH.get("secret_key"),
            "code": request.args.get("code"),
        },
        headers={"Accept": "application/json"},
    )
    res = res.json()
    if "error" in res:
        return redirect("/?error=%s" % res["error_description"])

    if "user:email" not in res["scope"].split(","):
        return redirect("/?error=user:email not in scope")

    session["access_token"] = res["access_token"]
    session["access_token_from"] = "github"
    user_info = user_info_from_github(session["access_token"])
    email_address = user_info["email"]
    users = UserService.query(email=email_address)
    user_id = get_uuid()
    if not users:
        # User isn't try to register
        try:
            try:
                avatar = download_img(user_info["avatar_url"])
            except Exception as e:
                logging.exception(e)
                avatar = ""
            users = user_register(
                user_id,
                {
                    "access_token": session["access_token"],
                    "email": email_address,
                    "avatar": avatar,
                    "nickname": user_info["login"],
                    "login_channel": "github",
                    "last_login_time": get_format_time(),
                    "is_superuser": False,
                },
            )
            if not users:
                raise Exception(f"Fail to register {email_address}.")
            if len(users) > 1:
                raise Exception(f"Same email: {email_address} exists!")

            # Try to log in
            user = users[0]
            login_user(user)
            return redirect("/?auth=%s" % user.get_id())
        except Exception as e:
            rollback_user_registration(user_id)
            logging.exception(e)
            return redirect("/?error=%s" % str(e))

    # User has already registered, try to log in
    user = users[0]
    user.access_token = get_uuid()
    login_user(user)
    user.save()
    return redirect("/?auth=%s" % user.get_id())


@manager.route("/feishu_callback", methods=["GET"])  # noqa: F821
def feishu_callback():
    """
    Feishu OAuth callback endpoint.
    ---
    tags:
      - OAuth
    parameters:
      - in: query
        name: code
        type: string
        required: true
        description: Authorization code from Feishu.
    responses:
      200:
        description: Authentication successful.
        schema:
          type: object
    """
    import requests

    app_access_token_res = requests.post(
        settings.FEISHU_OAUTH.get("app_access_token_url"),
        data=json.dumps(
            {
                "app_id": settings.FEISHU_OAUTH.get("app_id"),
                "app_secret": settings.FEISHU_OAUTH.get("app_secret"),
            }
        ),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    app_access_token_res = app_access_token_res.json()
    if app_access_token_res["code"] != 0:
        return redirect("/?error=%s" % app_access_token_res)

    res = requests.post(
        settings.FEISHU_OAUTH.get("user_access_token_url"),
        data=json.dumps(
            {
                "grant_type": settings.FEISHU_OAUTH.get("grant_type"),
                "code": request.args.get("code"),
            }
        ),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {app_access_token_res['app_access_token']}",
        },
    )
    res = res.json()
    if res["code"] != 0:
        return redirect("/?error=%s" % res["message"])

    if "contact:user.email:readonly" not in res["data"]["scope"].split():
        return redirect("/?error=contact:user.email:readonly not in scope")
    session["access_token"] = res["data"]["access_token"]
    session["access_token_from"] = "feishu"
    user_info = user_info_from_feishu(session["access_token"])
    email_address = user_info["email"]
    users = UserService.query(email=email_address)
    user_id = get_uuid()
    if not users:
        # User isn't try to register
        try:
            try:
                avatar = download_img(user_info["avatar_url"])
            except Exception as e:
                logging.exception(e)
                avatar = ""
            users = user_register(
                user_id,
                {
                    "access_token": session["access_token"],
                    "email": email_address,
                    "avatar": avatar,
                    "nickname": user_info["en_name"],
                    "login_channel": "feishu",
                    "last_login_time": get_format_time(),
                    "is_superuser": False,
                },
            )
            if not users:
                raise Exception(f"Fail to register {email_address}.")
            if len(users) > 1:
                raise Exception(f"Same email: {email_address} exists!")

            # Try to log in
            user = users[0]
            login_user(user)
            return redirect("/?auth=%s" % user.get_id())
        except Exception as e:
            rollback_user_registration(user_id)
            logging.exception(e)
            return redirect("/?error=%s" % str(e))

    # User has already registered, try to log in
    user = users[0]
    user.access_token = get_uuid()
    login_user(user)
    user.save()
    return redirect("/?auth=%s" % user.get_id())


def user_info_from_feishu(access_token):
    import requests

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {access_token}",
    }
    res = requests.get("https://open.feishu.cn/open-apis/authen/v1/user_info", headers=headers)
    user_info = res.json()["data"]
    user_info["email"] = None if user_info.get("email") == "" else user_info["email"]
    return user_info


def user_info_from_github(access_token):
    import requests

    headers = {"Accept": "application/json", "Authorization": f"token {access_token}"}
    res = requests.get(f"https://api.github.com/user?access_token={access_token}", headers=headers)
    user_info = res.json()
    email_info = requests.get(
        f"https://api.github.com/user/emails?access_token={access_token}",
        headers=headers,
    ).json()
    user_info["email"] = next((email for email in email_info if email["primary"]), None)["email"]
    return user_info


@manager.route("/logout", methods=["GET"])  # noqa: F821
@login_required
def log_out():
    current_user.access_token = f"INVALID_{secrets.token_hex(16)}"
    current_user.save()
    logout_user()
    return get_json_result(data=True)


@manager.route("/setting", methods=["POST"])  # noqa: F821
@login_required
def setting_user():
    update_dict = {}
    request_data = request.json
    if request_data.get("password"):
        new_password = request_data.get("new_password")
        if not check_password_hash(current_user.password, decrypt(request_data["password"])):
            return get_json_result(
                data=False,
                code=settings.RetCode.AUTHENTICATION_ERROR,
                message="Password error!",
            )

        if new_password:
            update_dict["password"] = generate_password_hash(decrypt(new_password))

    for k in request_data.keys():
        if k in [
            "password",
            "new_password",
            "email",
            "status",
            "is_superuser",
            "login_channel",
            "is_anonymous",
            "is_active",
            "is_authenticated",
            "last_login_time",
        ]:
            continue
        update_dict[k] = request_data[k]

    try:
        UserService.update_by_id(current_user.id, update_dict)
        return get_json_result(data=True)
    except Exception as e:
        logging.exception(e)
        return get_json_result(data=False, message="Update failure!", code=settings.RetCode.EXCEPTION_ERROR)


@manager.route("/info", methods=["GET"])  # noqa: F821
@login_required
def user_profile():
    """
    Get user profile information.
    ---
    tags:
      - User
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: User profile retrieved successfully.
        schema:
          type: object
          properties:
            id:
              type: string
              description: User ID.
            nickname:
              type: string
              description: User nickname.
            email:
              type: string
              description: User email.
    """
    return get_json_result(data=current_user.to_dict())


def rollback_user_registration(user_id):
    try:
        UserService.delete_by_id(user_id)
    except Exception:
        pass
    try:
        TenantService.delete_by_id(user_id)
    except Exception:
        pass
    try:
        u = UserTenantService.query(tenant_id=user_id)
        if u:
            UserTenantService.delete_by_id(u[0].id)
    except Exception:
        pass
    try:
        TenantLLM.delete().where(TenantLLM.tenant_id == user_id).execute()
    except Exception:
        pass


def user_register(user_id, user):
    user["id"] = user_id
    tenant = {
        "id": user_id,
        "name": user["nickname"] + "‘s Kingdom",
        "llm_id": settings.CHAT_MDL,
        "embd_id": settings.EMBEDDING_MDL,
        "asr_id": settings.ASR_MDL,
        "parser_ids": settings.PARSERS,
        "img2txt_id": settings.IMAGE2TEXT_MDL,
        "rerank_id": settings.RERANK_MDL,
    }
    usr_tenant = {
        "tenant_id": user_id,
        "user_id": user_id,
        "invited_by": user_id,
        "role": UserTenantRole.OWNER,
    }
    file_id = get_uuid()
    file = {
        "id": file_id,
        "parent_id": file_id,
        "tenant_id": user_id,
        "created_by": user_id,
        "name": "/",
        "type": FileType.FOLDER.value,
        "size": 0,
        "location": "",
    }
    tenant_llm = []
    for llm in LLMService.query(fid=settings.LLM_FACTORY):
        tenant_llm.append(
            {
                "tenant_id": user_id,
                "llm_factory": settings.LLM_FACTORY,
                "llm_name": llm.llm_name,
                "model_type": llm.model_type,
                "api_key": settings.API_KEY,
                "api_base": settings.LLM_BASE_URL,
                "max_tokens": llm.max_tokens if llm.max_tokens else 8192,
            }
        )
    if settings.LIGHTEN != 1:
        for buildin_embedding_model in settings.BUILTIN_EMBEDDING_MODELS:
            mdlnm, fid = TenantLLMService.split_model_name_and_factory(buildin_embedding_model)
            tenant_llm.append(
                {
                    "tenant_id": user_id,
                    "llm_factory": fid,
                    "llm_name": mdlnm,
                    "model_type": "embedding",
                    "api_key": "",
                    "api_base": "",
                    "max_tokens": 1024 if buildin_embedding_model == "BAAI/bge-large-zh-v1.5@BAAI" else 512,
                }
            )

    if not UserService.save(**user):
        return
    TenantService.insert(**tenant)
    UserTenantService.insert(**usr_tenant)
    TenantLLMService.insert_many(tenant_llm)
    FileService.insert(file)
    return UserService.query(email=user["email"])


@manager.route("/register", methods=["POST"])  # noqa: F821
@validate_request("nickname", "email", "password")
def user_add():
    """
    Register a new user.
    ---
    tags:
      - User
    parameters:
      - in: body
        name: body
        description: Registration details.
        required: true
        schema:
          type: object
          properties:
            nickname:
              type: string
              description: User nickname.
            email:
              type: string
              description: User email.
            password:
              type: string
              description: User password.
    responses:
      200:
        description: Registration successful.
        schema:
          type: object
    """

    if not settings.REGISTER_ENABLED:
        return get_json_result(
            data=False,
            message="User registration is disabled!",
            code=settings.RetCode.OPERATING_ERROR,
        )

    req = request.json
    email_address = req["email"]

    # Validate the email address
    if not re.match(r"^[\w\._-]+@([\w_-]+\.)+[\w-]{2,}$", email_address):
        return get_json_result(
            data=False,
            message=f"Invalid email address: {email_address}!",
            code=settings.RetCode.OPERATING_ERROR,
        )

    # Check if the email address is already used
    if UserService.query(email=email_address):
        return get_json_result(
            data=False,
            message=f"Email: {email_address} has already registered!",
            code=settings.RetCode.OPERATING_ERROR,
        )

    # Construct user info data
    nickname = req["nickname"]
    user_dict = {
        "access_token": get_uuid(),
        "email": email_address,
        "nickname": nickname,
        "password": decrypt(req["password"]),
        "login_channel": "password",
        "last_login_time": get_format_time(),
        "is_superuser": False,
    }

    user_id = get_uuid()
    try:
        users = user_register(user_id, user_dict)
        if not users:
            raise Exception(f"Fail to register {email_address}.")
        if len(users) > 1:
            raise Exception(f"Same email: {email_address} exists!")
        user = users[0]
        login_user(user)
        return construct_response(
            data=user.to_json(),
            auth=user.get_id(),
            message=f"{nickname}, welcome aboard!",
        )
    except Exception as e:
        rollback_user_registration(user_id)
        logging.exception(e)
        return get_json_result(
            data=False,
            message=f"User registration failure, error: {str(e)}",
            code=settings.RetCode.EXCEPTION_ERROR,
        )


@manager.route("/tenant_info", methods=["GET"])  # noqa: F821
@login_required
def tenant_info():
    """
    Get tenant information.
    ---
    tags:
      - Tenant
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: Tenant information retrieved successfully.
        schema:
          type: object
          properties:
            tenant_id:
              type: string
              description: Tenant ID.
            name:
              type: string
              description: Tenant name.
            llm_id:
              type: string
              description: LLM ID.
            embd_id:
              type: string
              description: Embedding model ID.
    """
    try:
        tenants = TenantService.get_info_by(current_user.id)
        if not tenants:
            return get_data_error_result(message="Tenant not found!")
        return get_json_result(data=tenants[0])
    except Exception as e:
        return server_error_response(e)


@manager.route("/set_tenant_info", methods=["POST"])  # noqa: F821
@login_required
@validate_request("tenant_id", "asr_id", "embd_id", "img2txt_id", "llm_id")
def set_tenant_info():
    """
    Update tenant information.
    ---
    tags:
      - Tenant
    security:
      - ApiKeyAuth: []
    parameters:
      - in: body
        name: body
        description: Tenant information to update.
        required: true
        schema:
          type: object
          properties:
            tenant_id:
              type: string
              description: Tenant ID.
            llm_id:
              type: string
              description: LLM ID.
            embd_id:
              type: string
              description: Embedding model ID.
            asr_id:
              type: string
              description: ASR model ID.
            img2txt_id:
              type: string
              description: Image to Text model ID.
    responses:
      200:
        description: Tenant information updated successfully.
        schema:
          type: object
    """
    req = request.json
    try:
        tid = req.pop("tenant_id")
        TenantService.update_by_id(tid, req)
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)
