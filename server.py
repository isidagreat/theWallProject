from flask import Flask, render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "ohyeaatellmemore"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
mysql = connectToMySQL('logindb')


@app.route('/')
def index():
	return render_template("index.html")	

@app.route("/validate", methods=['POST'])
def emailCheck():

	query="SELECT * FROM users WHERE email = %(email)s;"
	data = {"email": request.form['email']}
	result = mysql.query_db(query,data)
	if request.form["fname"].isalpha() != True or len(request.form["fname"]) < 2 or request.form["fname"].isspace():
		flash("Name cannot contain numbers OR Be left blank")
		return redirect ("/")
	elif len(request.form["lname"]) < 2 or request.form["lname"].isalpha() != True or request.form["lname"].isspace():
		flash("last Name cannot contain numbers or be blank")
		return redirect("/")
	elif len(request.form["pword"]) < 8 or request.form["pword"].isspace():
		flash("Password should be more than 8 characters")
		return redirect("/")
	elif request.form["cpword"] != request.form["pword"]:
		flash("passwords do not match")
		return redirect("/")
	elif len(request.form["email"]) <1:
		flash("Email cannot be empty")
	elif not EMAIL_REGEX.match(request.form['email']):
		flash ("invalid Email")
		return redirect("/")
	if result:
		i = 0
		while i < len(result):
			if result[i]['email'] == request.form['email']:
				flash("Unable to Register")
				i = i + 1
				return redirect("/")
	else:
		pw_hash = bcrypt.generate_password_hash(request.form['pword'])
		print (pw_hash)
		flash("Valid Email!!!!!!!!!!!")
		query1="INSERT INTO users (first_name, last_name, email,password, created_at, updated_at) VALUES (%(first_name)s,%(last_name)s,%(email)s,%(password_hash)s,  NOW(), NOW());"
		data1 = {"first_name": request.form['fname'],
				"last_name": request.form['lname'],
				"email": request.form['email'],
				"password_hash": pw_hash
				}
		mysql.query_db(query1,data1)
		
	return redirect("/")

@app.route('/login', methods=['POST'])
def logIn():
	if len(request.form["email"]) < 1 or request.form["email"].isspace():
		flash("Email cannot be empty")
	if len(request.form["cpword"]) < 1 or request.form["cpword"].isspace():
		flash("Password field cannot be empty")
		return redirect("/")
	loginquery="SELECT * FROM users WHERE email = %(email)s;"
	data = {"email": request.form['email']}
	result = mysql.query_db(loginquery, data)
	print(result)
	if result:
		if bcrypt.check_password_hash(result[0]['password'], request.form['cpword']):
			session['userid'] = result[0]['id']
			session['name'] = result[0]['first_name']
		return redirect("/wall")
	flash("You could not be logged in")	
	return redirect("/")

@app.route("/userpost", methods=['POST'])
def submitpost():
	if len(request.form["userpost"]) < 1 or request.form["userpost"].isspace():
		flash("Cannot submit empty posts")
		return redirect ("/wall")
	query1="INSERT INTO messages (message, created_at, updated_at,users_id) VALUES (%(message)s,  NOW(), NOW(), %(users_id)s);"
	data1 = {"message": request.form['userpost'],
			"users_id": session['userid']
			}
	mysql.query_db(query1,data1)
	return redirect("/wall")

@app.route("/comment", methods=['POST'])
def submitcomment():
	if len(request.form["usercomment"]) < 1 or request.form["usercomment"].isspace():
		flash("Cannot submit empty comments")
		return redirect ("/wall")
	query1="INSERT INTO comments (comment, created_at, updated_at,users_id, messages_id) VALUES (%(comment)s,  NOW(), NOW(), %(users_id)s, %(messages_id)s);"
	data1 = {"comment": request.form['usercomment'],
			"users_id": session['userid'],
			"messages_id": request.form['comment_id']
			}
	mysql.query_db(query1,data1)
	return redirect("/wall")

app.route("/removecomment", methods=['POST'])
def removecomment():
	if session['userid'] != request.form['delconfirm']:
		flash("cannot delete message")
		return redirect("/wall")
	query1="DELETE FROM comments WHERE id= %(id)s;"
	data1 = {'id': session['userid']}
	mysql.query_db(query1, data1)
	return redirect("/wall")

@app.route("/wall")
def displayWall():
	if 'userid' not in session:
		return redirect("/")
	# Can be reduced to one query
	query1="SELECT users.id, users.first_name, users.last_name, messages.message ,messages.created_at, messages.id AS m_id FROM messages Join users ON messages.users_id = users.id ORDER BY messages.created_at DESC;"
	result = mysql.query_db(query1)
	query2 ="SELECT comments.id, comments.comment, comments.created_at, comments.messages_id, users.first_name, users.last_name, users.id  FROM comments JOIN users ON comments.users_id = users.id;"
	result2 = mysql.query_db(query2)
	print("***************")
	print(session['userid'])
	print("****************")
	
	
	return render_template("/wall.html", result=result, result2=result2, length =len(result), length2=len(result2))


@app.route('/logout', methods=['POST'])
def logOut():
	session.clear()
	return redirect("/")	

if __name__ == "__main__":
	app.run(debug=True)







