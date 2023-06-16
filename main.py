import uvicorn

from src.app import abandon, dao
from config import AbandonConfig


if __name__ == "__main__":
    uvicorn.run(app=abandon, host=AbandonConfig.SERVER_HOST, port=AbandonConfig.SERVER_PORT)