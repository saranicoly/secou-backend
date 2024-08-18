import os
import pyrebase

firebaseConfig = {
    "apiKey": os.environ['SECOU_API_KEY'],
    "authDomain": "secou-f17a0.firebaseapp.com",
    "projectId": "secou-f17a0",
    "storageBucket": "secou-f17a0.appspot.com",
    "messagingSenderId": "10158890",
    "appId": "1:10158890:web:15f2965a88d5e019a51453",
    "databaseURL": "https://secou-f17a0-default-rtdb.firebaseio.com"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()
