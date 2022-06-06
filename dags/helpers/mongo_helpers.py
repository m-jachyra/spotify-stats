def get_database():
    from pymongo import MongoClient
    import pymongo

    CONNECTION_STRING = 'mongodb://root:example@mongo:27017'

    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    return client['spotify']

def save_data(data: dict, container_name: str):
        from pymongo import MongoClient
        import pymongo

        db = get_database()
        container = db[container_name]
        container.insert_many(data)
