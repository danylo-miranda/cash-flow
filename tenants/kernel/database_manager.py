from tenants.infrastructure.database.factory import DatabaseFactory


class DatabaseManager:

    def __init__(self):

        pass

    def connect(self):

        raise NotImplementedError

    def disconnect(self):

        raise NotImplementedError