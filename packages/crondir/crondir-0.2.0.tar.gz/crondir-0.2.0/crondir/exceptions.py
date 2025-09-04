from click import ClickException


class CrondirError(ClickException):
    pass


class CrontabError(CrondirError):
    pass
