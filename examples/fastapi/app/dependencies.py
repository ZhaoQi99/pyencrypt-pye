from fastapi import HTTPException


def check_license() -> None:
    try:
        import loader

        file_loader = loader.EncryptFileLoader("")
        if file_loader.license is True:
            file_loader.check()
    except ModuleNotFoundError:
        pass
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
