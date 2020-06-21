#FLASK_APP=app.py FLASK_ENV=development flask run --port 4040

from flask import Flask, render_template, url_for, request, redirect, flash, session, jsonify, send_file
import pyrebase
import json
import stripe
import pandas as pd
import csv
import codecs

app = Flask(__name__)
app.secret_key = '#d\xe9X\x00\xbe~Uq\xebX\xae\x82\x1fs\t\xb4\x99\xa3\x87\xe6.\xd1_'

stripe_pubkey = 'pk_test_CE8nMK2uLGoqKKytuATwYtsL00i6BheH2R'
stripe_secret = 'sk_test_7cXNsOpzonINjFFbtYZWI3Hy00yPATKKPb'
stripe.api_key = stripe_secret

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
auth = firebase.auth()

db = firebase.database()

from firebase import firebase
userDatabase = firebase.FirebaseApplication('https://sherrandsweb.firebaseio.com/userInfo')
groceryDatabase = firebase.FirebaseApplication('https://sherrandsweb.firebaseio.com/groceryCartData')
inventoryDatabase = firebase.FirebaseApplication('https://sherrandsweb.firebaseio.com/inventoryData')

approvedStoreList = ["Any Store", "Walmart", "Target", "Kroger"]

def idGivenEmail(email):
    listVersionOfEmail = list(email) 
    for i in range(0, len(listVersionOfEmail)):
        if listVersionOfEmail[i] == '.':
            listVersionOfEmail[i] = '1'
        elif listVersionOfEmail[i] == '*':
            listVersionOfEmail[i] = '2'
    email = "".join(listVersionOfEmail)
    return email

@app.route('/', methods=['GET'])
def home():
    if 'user' in session and session['AccountType'] == 'Business':
        return redirect('/addItem')
    elif 'user' in session:
         return redirect('/userScreen')
    return render_template('index.html', signInStatus="Sign In")

@app.route('/userScreen', methods=['GET'])
def userScreen():
    groceryDataList = getGroceryData()
    print(groceryDataList)
    return render_template('home.html', neigh= session['resCollege'],userNameForFilter=session['user'], approvedStoreList=approvedStoreList, tasks=groceryDataList, pubkey = stripe_pubkey)
def getGroceryData():
    groceryDataDict = groceryDatabase.get('/groceryCartData', None)
    groceryDataList = []
    if groceryDataDict != None:
        groceryDataList = [value for value in groceryDataDict.values()]
    return groceryDataList

@app.route('/search', methods=['GET'])
def search():
    imageSrcList = [{"url": "https://hips.hearstapps.com/hmg-prod/images/pumpkin-chocolate-chip-cookies-horizontal-1529964207.jpg", "label": "cookies"}, {"url": "https://duncanhines.com/sites/g/files/qyyrlu736/files/images/products/chewy-fudge-brownie-mix-15600.png", "label": "brownies"}] * 6
    return render_template('search.html', imageSrcList=imageSrcList, initItem="cookie")

@app.route('/searchStageTwo/<imageLabel>')
def searchStageTwo(imageLabel):
    return imageLabel

@app.route('/addItem', methods=['GET', 'POST'])
def addItem():
    if request.method == 'GET':
        inventoryDataList = getInventoryData()
        if not 'user' in session or not session['AccountType'] == 'Business':
            return redirect('/')
        return render_template('addItem.html', signInStatus = "Sign Out", tasks=inventoryDataList, nameOfStore=session['nameOfStore'])
    else:
        prodStore = session['nameOfStore']
        prodName = request.form['name']
        prodSize = request.form['size']
        try:
            prodPrice = float(request.form['price'])
        except:
            return redirect('/addItems#inventory')
        try:
            prodQuantity = int(request.form['quantity'])
        except:
            prodQuantity = 1
        prod_var = {"Store":prodStore, "Name":prodName, "Price":prodPrice, "Size":prodSize, "Quantity":prodQuantity}
        db.child("inventoryData").child(str(prodStore+prodName+prodSize)).set(prod_var)
        # db.child(prodStore).child(str(prodName+prodSize)).set(prod_var)
        return redirect('/addItem#inventory')
def getInventoryData():
    inventoryDataDict = inventoryDatabase.get('/inventoryData', None)
    inventoryDataList = []
    if inventoryDataDict != None:
        inventoryDataList = [value for value in inventoryDataDict.values()]
    return inventoryDataList

@app.route('/download', methods=['POST'])
def download():
    path = "Template.csv"
    return send_file(path, as_attachment=True)


@app.route('/addItemCSV/<store>', methods=['POST'])
def addItemCSV(store):
    flask_file = request.files['csvfile']
    if not flask_file:
        return redirect("/addItem#inventory")
    data = []
    stream = codecs.iterdecode(flask_file.stream, 'utf-8')
    try:
        for row in csv.reader(stream, dialect=csv.excel):
            if row:
                data.append(row)
    except UnicodeDecodeError:
        return redirect('/addItem#inventory')
    prodStore = store
    for i in range(1, len(data)):
        try:
            prodName = data[i][0]
            
            try:
                prodPrice = float(data[i][1])
            except:
                break

            prodSize = data[i][2]
            
            try:
                prodQuantity = int(data[i][3])
            except:
                prodQuantity = 1
        except:
            break
        prod_var = {"Store":prodStore, "Name":prodName, "Price":prodPrice, "Size":prodSize, "Quantity":prodQuantity}
        db.child("inventoryData").child(str(prodStore+prodName+prodSize)).set(prod_var)
    return redirect('/addItem#inventory')


@app.route('/addToGroceryList', methods=['POST'])
def addToGroceryList():
    inventoryDataList = getInventoryData()
    searchStore = request.form['store']
    initItem = request.form['item_info']
    try:
        qntyWanted = int(request.form['quantity'])
    except:
        qntyWanted = 1
    return render_template('lookUp.html', tasks=inventoryDataList, approvedStoreList=approvedStoreList, searchStore=searchStore, qntyWanted=qntyWanted, initItem=initItem) 

@app.route('/addToList/<store>/<prodName>/<sizeOfGood>/<qntyWanted>')
def addToList(store, prodName, sizeOfGood, qntyWanted):
    elmToSearch = store + prodName + sizeOfGood
    prodDict = inventoryDatabase.get('/inventoryData', elmToSearch)
    if prodDict != None:
        prodDict['user'] = session['user']
        prodDict['resCollege'] = session['resCollege']
        prodDict['qntyWanted'] = qntyWanted
    elmToAdd = idGivenEmail(session['user']) + elmToSearch
    try: 
        db.child("groceryCartData").child(elmToAdd).set(prodDict)
    except:
        print("Could not update element")
    return redirect('/userScreen#groceryList')

@app.route('/delete/<store>/<nameOfGood>/<sizeOfGood>', methods=['GET', 'POST'])
def delete(store, nameOfGood, sizeOfGood):
    elmToDelete = idGivenEmail(session['user']) + store + nameOfGood + sizeOfGood
    try: 
        inventoryDatabase.delete('/groceryCartData', elmToDelete)
    except:
        print("Could not delete element")
    return redirect('/userScreen#groceryList')

@app.route('/deleteProd/<nameOfGood>/<sizeOfGood>', methods=['GET', 'POST'])
def deleteProd(nameOfGood, sizeOfGood):
    elmToDelete = session['nameOfStore'] + nameOfGood + sizeOfGood
    print(elmToDelete)
    try: 
        inventoryDatabase.delete('/inventoryData', elmToDelete)
    except:
        print("Could not delete element")
    return redirect('/addItem#inventory')

@app.route('/update', methods=['GET', 'POST'])
def update():
    storeVal = request.form['storeName']
    nameOfGood = request.form['prod']
    sizeOfGood = request.form['size']
    origQty = request.form['origQty']
    try:
        quantityUpdate = int(request.form['quantity'])
    except:
        print("invalid quantity")
        return redirect('/userScreen#groceryList')

    elmToUpdateBase = storeVal + nameOfGood + sizeOfGood
    elmToUpdateOne = idGivenEmail(session['user']) + elmToUpdateBase
    updateDict = {'qntyWanted': quantityUpdate}
    try: 
        db.child("groceryCartData").child(elmToUpdateOne).update(updateDict)
    except:
        print("Could not update element")
    return redirect('/userScreen#groceryList')

@app.route('/copy/<store>/<prodName>/<sizeOfGood>/<int:qntyWanted>')
def copy(store, prodName, sizeOfGood, qntyWanted):
    elmToSearch = store + prodName + sizeOfGood
    prodDict = inventoryDatabase.get('/inventoryData', elmToSearch)
    if prodDict != None:
        prodDict['user'] = session['user']
        prodDict['resCollege'] = session['resCollege']
        prodDict['qntyWanted'] = qntyWanted
    elmToAdd = idGivenEmail(session['user']) + elmToSearch
    try: 
        db.child("groceryCartData").child(elmToAdd).set(prodDict)
    except:
        print("Could not update element")
    return redirect('/userScreen#groceryList')


@app.route('/updateProd', methods=['GET', 'POST'])
def updateProd():
    nameOfGood = request.form['orgProdName']
    sizeOfGood = request.form['orgProdSize']
    elmToDelete = session['nameOfStore'] + nameOfGood + sizeOfGood
    inventoryDatabase.delete('/inventoryData', elmToDelete)

    nameUpdate = request.form['name']
    sizeUpdate = request.form['size']
    try: 
        quantityUpdate = int(request.form['quantity'])
        priceUpdate = float(request.form['price'])
    except:
        print("invalid input")
        return redirect('/addItem#inventory')
    
    updateDict = {'Name': nameUpdate, 'Price': priceUpdate, 'Quantity': quantityUpdate, 'Size': sizeUpdate, 'Store': session['nameOfStore']}
    elmToUpdate = session['nameOfStore'] + nameUpdate + sizeUpdate
    try: 
        db.child("inventoryData").child(elmToUpdate).update(updateDict)
    except:
        print("Could not update element")
    return redirect('/addItem#inventory')


@app.route('/login', methods=['GET', 'POST'])
def logIn():
    if request.method == 'GET':
        return render_template('signIn.html')
       
    else: 
        #get email and password from html form
        email = request.form['email']
        password = request.form['password']
        
        #try loggin using oAuth from firebase
        try:
            user = auth.sign_in_with_email_and_password(email, password)
        except:
            return render_template('signIn.html', errorMessage="Incorrect Email or Password")

        if auth.get_account_info(user['idToken'])['users'][0]['emailVerified'] == False:
            return render_template('signIn.html', errorMessage="Please Verify Your Email") 

        #add session['user'] for current user email
        session['user'] = auth.get_account_info(user['idToken'])['users'][0]['email']
        userData = userDatabase.get('/userInfo', None)[idGivenEmail(session['user'])]
        if userData['AccountType'] == 'Business':
            session['AccountType'] = 'Business'
            session['nameOfStore'] = userData['Names']
            session['address'] = userData['Address']
            return redirect('/addItem')
        session['AccountType'] = 'User'
        session['resCollege'] = userData['resCollege']
        return redirect('/') 

@app.route('/processSignUp', methods=['POST'])
def signUpProcess():
    userType = request.form['userType']
    if userType == "User":
        return redirect('/signUp')
    else:
        return redirect('/businessSignUp')

@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'GET':
        return render_template('createAccount.html',errorMessage="")
    else:
        name = request.form['name']
        email = request.form['email']
        resCollege = request.form['resCollege']
        dormAddress = request.form['dormAddress']
        password = request.form['password']
        passwordRepeat = request.form['passwordRepeat']

        if password != passwordRepeat:
            return render_template('createAccount.html', errorMessage="Passwords Do Not Match")
        try:
            user = auth.create_user_with_email_and_password(email, password)
        except Exception as e:
            fullErrorMessage = e.args[1]
            err = json.loads(fullErrorMessage)["error"]["message"]
            return render_template('createAccount.html', errorMessage=err)

        db.child("userInfo").child(idGivenEmail(email)).set({"Names": name, "Email": email, "AccountType": "User", "resCollege": resCollege, "dormAddress": dormAddress, "password":password})
        
        auth.send_email_verification(user['idToken'])

        return redirect('/')

@app.route('/businessSignUp', methods=['POST', 'GET']) 
def businessSignUp():
    if request.method == 'GET':
        return render_template('createBusinessAccount.html')
    else:    
        name = request.form['name']
        email_info = request.form['email']
        addy = request.form['address']
        password_info = request.form['password']
        repeat_pass = request.form['psw-repeat']
        if not password_info == repeat_pass:
            return "passwords don't match"
        
        if password_info != repeat_pass:
            return render_template('createBusinessAccount.html', errorMessage="Passwords Do Not Match")
        try:
            user = auth.create_user_with_email_and_password(email_info, password_info)
        except Exception as e:
            fullErrorMessage = e.args[1]
            err = json.loads(fullErrorMessage)["error"]["message"]
            return render_template('createBusinessAccount.html', errorMessage=err)

        db.child("userInfo").child(idGivenEmail(email_info)).set({"Names": name, "Email": email_info, "AccountType": "Business", "address": addy, "password":password_info})
        
        auth.send_email_verification(user['idToken'])

        return redirect('/')

@app.route('/signout')  
def sign_out():
    if 'user' not in session:
        return redirect('/')
    del session['user']
    if session['AccountType'] == 'Business':
        del session['address']
        del session['nameOfStore']
    else:
        del session['resCollege']
    del session['AccountType']
    return redirect('/')

# main driver function 
if __name__ == '__main__':   
    app.run(debug=True) 
