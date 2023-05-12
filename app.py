from flask import Flask, session, render_template, request, abort, redirect
import mysql.connector
import json
import uuid

app = Flask(__name__)
app.secret_key = ";"

database = mysql.connector.connect(
   host = "localhost",
   user = "root",
   password = "01015173zxcvB!",
   database = "spiral"
)


@app.route("/")
def Register():
   return render_template("Register.html")

@app.route("/createAccount", methods=["POST", "GET"])
def createAccount():

   name = request.form.get("name")
   email = request.form.get("email")
   username = request.form.get("username")
   password = request.form.get("password")

   if not username:
      abort(404)

   cursor = database.cursor()
   sql = '''
      INSERT into accounts (name, email, username, password, accountType)
      VALUES (%s,%s,%s,%s,%s)
   '''
   
   values = (name,email,username,password, "customer")
   cursor.execute(sql,values)
   database.commit()

   return "createAccount"

@app.route("/loginToAccount", methods=["POST"])
def loginToAccount():

   email = request.form.get("email")
   password = request.form.get("password")

   cursor = database.cursor()
   
   sql = '''
      SELECT * from accounts
      WHERE email = %s and password = %s
   '''
   values = (email, password)
   cursor.execute(sql, values)

   validUser =  cursor.fetchone()

   if validUser:
      print("Successfully logged in!")
      session["user"] = validUser
      if session["user"][5] == "customer":
         return "/Home"
      elif session["user"][5] == "vendor":
         return "/vendorHome"
   elif email == "admin" and password == "admin":
      return "/adminHome"
   else:
      return "/Error"

@app.route("/Login")
def Login():
   return render_template("Login.html")

@app.route("/Home")
def Home():
   return render_template("customerHome.html", user=session.get("user"))

@app.route("/Error")
def Error():
   return "Error, try again."

@app.route("/accountPage")
def accountPage():
   return render_template("accountPage.html", user=session.get("user"))

@app.route("/logout")
def logout():
   return render_template("Login.html")

@app.route("/changeAccountType", methods=["POST"])
def changeAccountType():

   chosenAccountType = request.form.get("type")
   
   cursor = database.cursor()
   sql = '''
      UPDATE accounts
      SET accountType = %s
      WHERE email = %s
      
   '''

   values = (chosenAccountType, session.get("user")[2])
   cursor.execute(sql, values)

   return "Changing Account Type"

@app.route("/vendorHome")
def vendorHome():

   if session.get("user"):

      with open("products.json", "r") as f:
         data = json.load(f)

      products = []

      for key in data:
         if data[key]["vendor"] == session.get("user")[2]:
            products.append(data[key])

      return render_template("vendorHome.html", products=products)
   else:
      return render_template("Login.html")

@app.route("/productCreator")
def productCreator():
   return render_template("productCreator.html")

@app.route("/createProduct", methods=["POST"])
def createProduct():

   title = request.form.get("title")
   description = request.form.get("description")
   image = request.form.get("image")
   category = request.form.get("category")
   colors = json.loads(request.form.get("colors"))
   sizes = json.loads(request.form.get("sizes"))
   stock = int(request.form.get("stock"))
   price = float(request.form.get("price"))

   with open("products.json", "r") as f:
      data = json.load(f)

   generatedID = str(uuid.uuid4())

   def setupProductData():

      productData = {
         "title" : title,
         "description" : description,
         "image" : image,
         "category" : category,
         "colors" : colors,
         "sizes" : sizes,
         "stock" : stock,
         "price" : price,
         "reviews" : {},
         "vendor" : session.get("user")[2],
         "productID" : generatedID
      }

      return productData

   if len(data) <= 0:
      
      data[generatedID] = setupProductData()

      with open('products.json', 'w') as f:
         json.dump(data, f, indent=4)

   else:

      data[generatedID] = setupProductData()

      with open('products.json', 'w') as f:
         json.dump(data, f, indent=4)

   return "Created Product!"

@app.route("/deleteProduct", methods=["POST"])
def deleteProduct():

   productID = request.form.get("productID")

   with open("products.json", "r") as f:
      data = json.load(f)

   data.pop(productID, None)

   with open('products.json', 'w') as f:
         json.dump(data, f, indent=1)

   return "Deleted Product!"

@app.route("/edit", methods=["POST", "GET"])
def edit():

   with open("products.json", "r") as f:
      data = json.load(f)

   productID = request.args.get("productID")
   productData = data[productID]
   return render_template("productEditor.html", productData=productData)

@app.route("/editComplete", methods=["POST"])
def editComplete():
   productID = request.form.get("productID")
   newTitle = request.form.get("newTitle")
   newDescription = request.form.get("newDescription")
   newImage = request.form.get("newImage")
   newCategory = request.form.get("newCategory")
   newPrice = float(request.form.get("newPrice"))

   with open("products.json", "r") as f:
      data = json.load(f)

   data[productID]["title"] = newTitle
   data[productID]["description"] = newDescription
   data[productID]["image"] = newImage
   data[productID]["category"] = newCategory
   data[productID]["price"] = newPrice

   with open('products.json', 'w') as f:
         json.dump(data, f, indent=4)

   return "Editing Complete"

@app.route("/adminHome")
def adminHome():

   with open("products.json", "r") as f:
      data = json.load(f)

   products = []

   for key in data:
      products.append(data[key])
   
   return render_template("adminHome.html", products=products)


@app.route("/productPage")
def productPage():

   with open("products.json", "r") as f:
      data = json.load(f)

   productID = request.args.get("productID")
   productData = data[productID]

   return render_template("productPage.html", productData=productData)