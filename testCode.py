from firebase_admin import db
import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyDRjXyJgAAq_iWO_B5raLiblkuGRTFXVkw",
    "authDomain": "sherrandsweb.firebaseapp.com",
    "databaseURL": "https://sherrandsweb.firebaseio.com",
    "projectId": "sherrandsweb",
    "storageBucket": "sherrandsweb.appspot.com",
    "messagingSenderId": "509206998566",
    "appId": "1:509206998566:web:b6f70086deebc29f2900e7",
    "measurementId": "G-1LSZM8TWQ8"
}

firebase = pyrebase.initialize_app(firebaseConfig)
# auth = firebase.auth()

db = firebase.database()

db.child("inventoryData").child("WalmartCookies32 Pack").update({'Name': 'Cookie', 'Price': 2.34, 'Quantity': 523, 'Size': '32 Pack', 'Store': 'Walmart'})

# b = {"AccountType": "Business", "Email": "kingraj987@gmail.com", "Names": "Walart", "Address": "31118 Lindenteee Drive", "password":"password"}
# db.child("userInfo").child(idGivenEmail("kingraj987@gmail.com")).set(b)

from firebase import firebase
fireb = firebase.FirebaseApplication('https://sherrandsweb.firebaseio.com/inventoryData')

# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://sherrandsweb.firebaseio.com/'
# })

# ref = db.reference('/inventoryData/WalmartCookies32 Pack')
# result = ref.update({'Name': 'Cookies', 'Price': 2.34, 'Quantity': 523, 'Size': '32 Pack', 'Store': 'Walmart'})
# print(result)