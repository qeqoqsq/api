from datetime import datetime

from pydantic import BaseModel, EmailStr
# ===== Pydantic-модели =====
class RegisterData(BaseModel):
    login: str
    password: str
    ip_address: str
    email: str

class CheckUniqueLogin(BaseModel):
    login: str

class LoginData(BaseModel):
    login: str
    password: str

class KeyCreateRequest(BaseModel):
    key_duration: int

class KeyActivateRequest(BaseModel):
    key_value: str
    user_id: int

class GetUserInfo(BaseModel):
    user_id: int

class CheckSubscriptionStatus(BaseModel):
    user_id: int
    token: str

class CheckValidLaunchToken(BaseModel):
    user_id: int
    sub_token: str
    launch_token: str

class EmailRequest(BaseModel):
    email: EmailStr

class CodeConfirmRequest(BaseModel):
    email: EmailStr
    code: str

class UserInfo(BaseModel):
    user_login: str
    email: str
    ip_address: str
    subscribe_status: bool
    subscription_end_date: str

class ChangePassword(BaseModel):
    login: str
    current_password: str
    new_password: str

class TokenCheckRequest(BaseModel):
    token: str