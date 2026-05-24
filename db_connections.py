# MongoDB Database Connection
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import config

# Use MongoClient to set up mongodb connection
username = config.username
password = config.password
cluster = 'ml-analytics-cluster.qkmsm.mongodb.net'

cloudstr_uri = f'mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority'
mogodb_client = MongoClient(cloudstr_uri, server_api=ServerApi('1'))
#db = mogodb_client['Final_Project']
#terrorism = db["terrorism"]

# Send a ping to confirm a successful connection
try:
    mogodb_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)