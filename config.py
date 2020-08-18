import os

class Config(object):
    SECRET_KEY          = os.environ.get('SECRET_KEY') or "asdfaqw37894598wergfjkdf"

    MONGODB_SETTINGS    = {'db' : 'book_shop', 'host' : 'mongodb+srv://root:Zee9Zee9@firstcluster.qhtcj.mongodb.net/book_shop?retryWrites=true&w=majority'

    }
