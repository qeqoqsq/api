import models
import key_logic
import get_tables
import authentication
import subscription_functions
import email_messages
import user_info_logic
import change_user_info
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
async def get_users():
    print("get users")
    return await get_tables.get_users()

@router.get("/subscriptions")
async def get_subscriptions():
    print("get subscriptions")
    return await get_tables.get_subscriptions()

# @router.get("/license-keys")
# async def get_license_keys():
#     print("get license-keys")
#     return await get_tables.get_license_keys()

@router.post("/check-unique-login")
async def check_unique_login(request: models.CheckUniqueLogin):
    print("check-unique-login")
    return await authentication.check_unique_login(request)

# Функция регистрации
@router.post("/register")
async def register_user(request: models.RegisterData):
    print("register")
    return await authentication.register_user(request)

# Функция авторизации
@router.post("/login")
async def login_user(request: models.LoginData):
    print("login")
    return await authentication.login_user(request)

@router.post("/create-key")
async def create_license_key(request: models.KeyCreateRequest):
    print("create-key")
    return await key_logic.create_license_key(request)

@router.post("/activate-key")
async def activate_license_key(request: models.KeyActivateRequest):
    print("activate-key")
    return await key_logic.activate_license_key(request)

@router.post("/get-subscription-status")
async def get_subscription_status(request: models.CheckSubscriptionStatus):
    print("get-subscription-status")
    return await subscription_functions.get_subscription_status(request)

@router.post("/send-code")
async def send_code(request: models.EmailRequest):
    print("send-code")
    return await email_messages.send_code(request)

@router.post("/confirm-code")
async def confirm_code(request: models.CodeConfirmRequest):
    print("confirm-code")
    return await email_messages.confirm_code(request)

@router.post("/get-user-info")
async def get_user_info(request: models.GetUserInfo):
    print("get-user-info")
    return await user_info_logic.get_user_info(request)

@router.post("/change-user-password")
async def change_user_password(request: models.ChangePassword):
    print("change-user-password")
    return await change_user_info.change_user_password(request)

@router.post("/validate-token")
async def validate_token(request: models.TokenCheckRequest):
    print("validate-token")
    return await authentication.validate_token(request)

@router.post("/check-valid-launch-token")
async def check_valid_launch_token(request: models.CheckValidLaunchToken):
    print("check-valid-launch-token")
    return await subscription_functions.check_valid_launch_token(request)
