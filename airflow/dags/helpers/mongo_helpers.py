def get_database():
    from pymongo import MongoClient
    import pymongo

    CONNECTION_STRING = 'mongodb://root:example@localhost:27017'

    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    return client['spotify']