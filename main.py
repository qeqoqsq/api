from fastapi import FastAPI
from routes import router
from fastapi.responses import FileResponse

app = FastAPI()

version_number: str = "1.3.0"

@app.get("/")
async def root():
    print("Проверка маршрута")
    return {"status": "API работает"}

@app.on_event("startup")
async def startup_event():
    print("Приложение запускается...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Приложение завершает работу...")

# Версия лаунчера
@app.get("/launcher/version")
def get_version():
    return {"version": version_number}

# Скачивание архива
@app.get("/launcher/download")
def download_launcher():
    return FileResponse("files/launcher_update.zip", filename="launcher_update.zip")

# Подключаем роутер с эндпоинтами
app.include_router(router)