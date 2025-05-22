import smtplib


def check_yandex_smtp_login(email: str, app_password: str) -> bool:
    """
    Проверяет возможность входа на SMTP-сервер Яндекса с указанными учетными данными.

    :param email: Адрес электронной почты Яндекса.
    :param app_password: Пароль приложения (app password).
    :return: True если вход успешен, False если нет.
    """
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email, app_password)
        return True
    except smtplib.SMTPAuthenticationError:
        return False
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False


# Пример использования

email = "NeScumContora2009@gmail.com"
app_password = "uxwu szgo rpls klqj"
if check_yandex_smtp_login(email, app_password):
    print("Вход успешен!")
else:
    print("Ошибка аутентификации. Проверьте email и пароль приложения.")
