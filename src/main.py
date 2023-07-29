if __name__ == '__main__':
    import uvicorn

    from app import build_app
    from config import CONFIG

    uvicorn.run(build_app(), port=CONFIG.port)
