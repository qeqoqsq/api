import smtplib
import os
import models
import other_functions
from dotenv import load_dotenv
from email.message import EmailMessage
from fastapi import HTTPException

load_dotenv()
confirmation_codes = {}

def send_confirmation_email(to_email: str, confirmation_code: str):
    # Настройки отправителя
    sender_email = os.getenv("sender_email")
    print(sender_email)
    sender_password = os.getenv("sender_password")
    print(sender_password)
    # Текст письма
    subject = "Подтверждение регистрации"
    body = f"""
    Здравствуйте!

    Спасибо за ваши деньги. Ваш код подтверждения: {confirmation_code}

    Введите его в приложении для завершения регистрации.
    """

    # Формируем письмо
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    msg.set_content(body)

    # Отправляем через SMTP Gmail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


async def send_code(request: models.EmailRequest):
    code = other_functions.generate_confirmation_code()
    confirmation_codes[request.email] = code
    try:
        send_confirmation_email(request.email, code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отправки письма: {e}")
    return {"message": "Код отправлен на почту"}

async def confirm_code(request: models.CodeConfirmRequest):
    real_code = confirmation_codes.get(request.email)
    if real_code is None:
        raise HTTPException(status_code=404, detail="Код для данного email не найден")
    if real_code != request.code:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")
    # При успешном подтверждении можно удалить код или сделать отметку
    del confirmation_codes[request.email]
    return {"message": "Почта успешно подтверждена"}