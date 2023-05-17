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

   with open("extra/products.json", "r") as f:
      data = json.load(f)

   products = []

   for key in data:
      products.append(data[key])

   return render_template("customerHome.html", user=session.get("user"), products=products)

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

      with open("extra/products.json", "r") as f:
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

   with open("extra/products.json", "r") as f:
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

      with open('extra/products.json', 'w') as f:
         json.dump(data, f, indent=4)

   else:

      data[generatedID] = setupProductData()

      with open('extra/products.json', 'w') as f:
         json.dump(data, f, indent=4)

   return "Created Product!"

@app.route("/deleteProduct", methods=["POST"])
def deleteProduct():

   productID = request.form.get("productID")

   with open("extra/products.json", "r") as f:
      data = json.load(f)

   data.pop(productID, None)

   with open('extra/products.json', 'w') as f:
         json.dump(data, f, indent=1)

   return "Deleted Product!"

@app.route("/edit", methods=["POST", "GET"])
def edit():

   with open("extra/products.json", "r") as f:
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

   with open("extra/products.json", "r") as f:
      data = json.load(f)

   data[productID]["title"] = newTitle
   data[productID]["description"] = newDescription
   data[productID]["image"] = newImage
   data[productID]["category"] = newCategory
   data[productID]["price"] = newPrice

   with open('extra/products.json', 'w') as f:
         json.dump(data, f, indent=4)

   return "Editing Complete"

@app.route("/adminHome")
def adminHome():

   with open("extra/products.json", "r") as f:
      data = json.load(f)

   products = []

   for key in data:
      products.append(data[key])
   
   return render_template("adminHome.html", products=products)

@app.route("/productPage")
def productPage():

   with open("extra/products.json", "r") as f:
      data = json.load(f)

   productID = request.args.get("productID")
   productData = data[productID]

   return render_template("productPage.html", productData=productData)

@app.route("/addToCart", methods=["POST"])
def addToCart():

   productID = request.form.get("productID")
   color = request.form.get("color")
   size = request.form.get("size")
   
   with open("extra/carts.json", "r") as f:
      carts = json.load(f)

   with open("extra/products.json", "r") as f:
      data = json.load(f)

   generatedID = str(uuid.uuid4())
   
   if session.get("user")[2] in carts:
      carts[session.get("user")[2]].update({
         generatedID : [generatedID,color,size, data[productID]['price'], data[productID]['image'], data[productID]['title']]
      })
      carts[session.get("user")[2]]['total'] += data[productID]['price']
   else:
      carts[session.get("user")[2]] = {
         generatedID : [generatedID, color, size, data[productID]['price'], data[productID]['image'], data[productID]['title']],
         "total" : data[productID]['price']
      }
   
   with open('extra/carts.json', 'w') as f:
         json.dump(carts, f, indent=4)

   return "Add Product To Cart"

@app.route("/cart")
def cart():

   with open("extra/carts.json", "r") as f:
      carts = json.load(f)

   items = []
   total = 0

   for email in carts:
      if email == session.get("user")[2]:
         for itemInfo in carts[email]:
            if itemInfo == "total":
               total = carts[email][itemInfo]
               continue
            items.append(carts[email][itemInfo])
   

   return render_template("cart.html", items=items,total=total)

@app.route("/thank")
def thank():

   order_number = uuid.uuid4().hex

   with open("extra/orders.json", "r") as f:
      orders = json.load(f)

   with open("extra/carts.json", "r") as f:
      carts = json.load(f)

   orders[order_number] = {
      "customer" : session.get("user")[2],
      "items" : []
   }

   for key in carts:
      if key == session.get("user")[2]:
         for item in carts[key]:
            if item != 'total':
               orders[order_number]["items"].append(carts[key][item])
               
   carts.pop(session.get("user")[2], None)

   with open('extra/orders.json','w') as f:
      json.dump(orders, f, indent=4)

   with open('extra/carts.json','w')as f:
      json.dump(carts, f, indent=4)

   return render_template("thank.html", user=session.get("user"), order_number=order_number)

@app.route("/submitReview", methods=["POST"])
def submitReview():

   productID = request.form.get("productID")
   rating = request.form.get("rating")
   desc = request.form.get("desc")

   with open("extra/products.json", "r") as f:
      products = json.load(f)

   products[productID]["reviews"].append({
      "rating" : int(rating),
      "desc" : desc,
      "reviewer" : session.get("user")[1]
   })

   with open('extra/products.json','w') as f:
      json.dump(products, f, indent=4)

   return "New Review!"

@app.route("/filterReviews", methods=["POST"])
def filterReviews():

   with open("extra/products.json", "r") as f:
      products = json.load(f)
   
   productID = request.form.get("productID")

   products[productID]['reviews'].sort(key=lambda x: x['rating'], reverse=True)

   with open('extra/products.json','w') as f:
      json.dump(products, f, indent=4)

   return "Fitler Reviews"