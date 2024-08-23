import uvicorn
from fastapi import FastAPI

from app_infra.app import make_app


def main():
    app = FastAPI()
    make_app(app)
    uvicorn.run(app)


if __name__ == '__main__':
    main()
