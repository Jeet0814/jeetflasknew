from collections import UserString
from flask import Flask, make_response, redirect, render_template, url_for, session, request
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
connection_string = "mysql+mysqlconnector://root:1234@localhost/fllask_blogs"
engin = create_engine(connection_string, echo=True)

app= Flask(__name__)

app.secret_key = "flask_blogs"

app.config['UPLOAD_FOLDER'] = "static/images"

@app.route('/')
def home():
    with engin.connect() as conn:

        result = conn.execute(text("SELECT blogs.*, users.fname, users.lname FROM blogs JOIN users ON blogs.user_id"))
        blogs = []
        for row in result.all():
            blogs.append(row)

        print(blogs)
        return render_template("home.html", blogs = blogs,title="Home")

@app.route('/login', methods = ['POST', 'GET'])
def login():
    showAlert = False
    if request.method == 'GET':
        return render_template("login.html", showAlert = showAlert, title = "Login Page")
    elif request.method == 'POST':
        data = request.form
        # print(data)
        with engin.connect() as conn:
            query = "SELECT * FROM users WHERE email = :email AND password = :password"
            result=conn.execute(text(query),{
                "email" : data["email"],
                "password" : data["password"]
            })
            if result.rowcount == 1:
                session['user_id'] = result.all()[0][0]
                # print(result)
                return redirect(url_for('home'))
        
        showAlert = True
        return render_template("login.html", showAlert = showAlert)
    
@app.route('/registration', methods = ['POST' , 'GET'])
def registration():
    if request.method == 'GET':  
        return render_template("registration.html", title="Registration Page")
    elif request.method == 'POST':
        data = request.form 
    with engin.connect() as conn:   
        query = "INSERT INTO users(fname, lname, email, password, address, state, city, zip) VALUES (:fname, :lname, :email, :password, :address, :state , :city, :zip)"
        result=conn.execute(text(query),{

        "fname": data["fname"],
        "lname": data["lname"],
        "email": data["email"],
        "password": data["password"],
        "address": data["address"],
        "city": data["city"],
        "state": data["state"],
        "zip": data["zip"]
        })

        conn.commit()
        
        if result.rowcount == 1:
            return redirect(url_for("login"))


    return render_template ('registration.html', title="Registration Page")
    
@app.route('/add_blogs', methods = ['POST', 'GET'])
def add_blogs():
    if request.method == 'GET':  
        return render_template("add_blogs.html", title="Add Blogs")
    elif request.method == 'POST':
        data = request.form
        image = request.files['image']
        imageName = image.filename
        user_id = session['user_id']
    with engin.connect() as conn:   
        query = "INSERT INTO blogs(title, description, image, user_id) VALUES (:title, :description, :image, :user_id)"
        result=conn.execute(text(query),{
            "title" : data["title"],
            "description" : data["description"],
            "image" : imageName,
            "user_id" : user_id
        })
        conn.commit()
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], imageName))
        print(result)
    return redirect(url_for('home'),  title = "Add Blogs")
        

@app.route('/myblogs', methods = ['POST', 'GET'])
def myblogs():
    query = "SELECT blogs.*,users.fname, users.lname FROM blogs JOIN users ON blogs.user_id = users.user_id WHERE blogs.user_id = :user_id"
    with engin.connect() as conn:   
        result=conn.execute(text(query),{
            "user_id" : session['user_id']
        })
        blogs = []
        for row in result.all():
            blogs.append(row)
    return render_template("myblogs.html", blogs=blogs)

@app.route('/blog_details/<blog_id>')
def blog_details(blog_id):
    query = "SELECT blogs.*, users.fname, users.lname FROM blogs JOIN users ON blogs.user_id = users.user_id WHere blogs.blog_id = :blog_id"
    with engin.connect() as conn:  
        result=conn.execute(text(query),{
            "blog_id" : blog_id
        })
        blog = result.first()
        return render_template("blog_details.html", blog = blog,  title="My Blogs")
    


    

@app.route('/profile')
def profile():
    
    query = "SELECT * FROM users WHERE user_id = :user_id"

    with engin.connect() as conn:   
       
        result=conn.execute(text(query),{
            "user_id": session["user_id"]
            })
        

        data = result.first()

        return render_template("profile.html", data = data,  title = "Profile")

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session.pop("user_id", None)
    return redirect(url_for('login'))

@app.route('/delete_blog/<blog_id>')
def delete_blog(blog_id):
    query = "DELETE FROM blogs WHERE blog_id = :blog_id"
    with engin.connect() as conn:   
        result=conn.execute(text(query),{
            "blog_id": blog_id
        })
        conn.commit()
        return redirect(url_for('myblogs'), title = "Login Page")

@app.route('/edit_blog/<blog_id>', methods = ['GET', 'POST'])
def edit_blog(blog_id):
    if request.method == 'GET':
        query = "SELECT blogs.*, users.fname, users.lname FROM blogs JOIN users ON blogs.user_id = users.user_id WHere blogs.blog_id = :blog_id"
        with engin.connect() as conn:  
            result=conn.execute(text(query),{
            "blog_id" : blog_id
        })
        blog = result.first() 

        return render_template('edit_blog.html', blog=blog, title = "Edit Blogs")
    if request.method == 'POST':
        data = request.form
        query = "UPDATE blogs SET title = :title, description = :description WHERE blog_id = :blog_id"
        with engin.connect() as conn:  
            result=conn.execute(text(query),{
                "title" : data['title'],
                "description" : data['description'],
                "blog_id" : blog_id
            })
            conn.commit()
            return redirect(url_for('myblogs'))
        
@app.route('/contact_us')
def contact_us():
    return render_template("contact_us.html", title="Contact Us")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')