from flask import Flask, render_template, request, flash, redirect, url_for, session

# import vertexai
# from vertexai.preview.language_models import TextGenerationModel
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
key_path="./static/assets/lablabai-406919-e0c47d25bf7d.json"
import sqlite3
# credentials=Credentials.from_service_account_file(key_path,scopes=["https://www.googleapis.com/auth/cloud-platform"])

# if credentials.expired:
#     credentials.refresh(Request())

# PROJECT_ID='lablabai-406919'
# REGION='us-central1'

# vertexai.init(project=PROJECT_ID, location=REGION,credentials=credentials)
# parameters = {
#     "max_output_tokens": 1024,
#     "temperature": 0.2,
#     "top_p": 0.8,
#     "top_k": 40
# }
# model = TextGenerationModel.from_pretrained("text-bison-32k")
# response = model.predict(
# """write for me a story for kids""",
# **parameters
# )
con=sqlite3.connect("database.sqlite")
cur = con.cursor()

# Modified table creation with an auto-incrementing primary key
cur.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        First_name TEXT,
        Last_name TEXT,
        email TEXT,
        password TEXT
    )
""")
cur.execute("""
       CREATE TABLE IF NOT EXISTS info (
        user_id INTEGER PRIMARY KEY,
        phone_number VARCHAR,
        photo BLOB,
        title TEXT,
        address TEXT,
        linkedin_profile TEXT,
        skills TEXT,
        languages TEXT,
        profile TEXT,
        education TEXT,
        professional_experience TEXT,
        interests TEXT,
        certificates TEXT,
        organizations TEXT,
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
    )
""")

# cur.execute("""
#        DELETE FROM user WHERE First_name = 'ines1' AND Last_name = 'ines1' AND email = 'ines1@gmail.com';
# """)

con.commit()
con.close()

app = Flask(__name__)
app.secret_key="123"
@app.route("/")
def home():
    return render_template("index_front.html")


@app.route("/editprofile", methods=['GET', 'POST'])
def editprofile():
    con = None  # Initialize con outside the try block

    if request.method == 'POST':
        try:
            
            if "update_button" in request.form:
                
                first_name = request.form['first_name']
                last_name = request.form['last_name']
                
                email = request.form['email']
                title = request.form['title']
                phone_number = request.form['phone_number']
                address = request.form['Adress']
                linkedin_p = request.form['linkedin_p']
                photo = request.files['photo']
                skills = request.form['Skills']
                languages = request.form['languages']
                profile = request.form['profile']
                education = request.form['Education']
                professional_experience = request.form['professional_experience']
                interests = request.form['interests']
               
                certificates = request.form['certificates']
                organizations = request.form['organizations']
                
                print(first_name)
                print(last_name)
                print(email)
                print(title)
                print(phone_number)
                print(linkedin_p)
                print(organizations)
                print(photo)
                print(title)
                con = sqlite3.connect("database.sqlite")
                cur = con.cursor()

                # Check if the user already exists
                cur.execute("SELECT id FROM user WHERE First_name=? AND Last_name=? AND email=?", (first_name, last_name, email))
                user_data = cur.fetchone()
                print(user_data)
                
                if user_data:
                    user_id = user_data[0]
                    print(user_id)
                    
                    # Save the photo to a variable as binary data
                    if photo and photo.filename != '':
                        photo_binary = photo.read()

                        # Insert the binary data into the database
                        cur.execute("""
                            INSERT INTO info (user_id, phone_number, linkedin_profile, title, photo, address, skills, languages, profile, education, professional_experience, interests, certificates, organizations)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (user_id, phone_number, linkedin_p, title, photo_binary, address, skills, languages, profile, education, professional_experience, interests, certificates, organizations))
                       
                        con.commit()
                        flash("Record Added Successfully", "success")
                else:
                    flash("User not found", "danger")

        except Exception as e:
            print(f"Error in Insert Operation: {e}")
            print('Exception occurred, insert not successful')
            flash(f"Error in Insert Operation: {e}", "danger")
        finally:
            if con is not None:
                con.close()

                # Redirect outside of the 'finally' block to ensure the connection is closed
                return redirect("editprofile")

    return render_template('editprofile.html')




@app.route('/login',methods=["GET","POST"])
def login():
    error_message = None  # Initialize error_message variable

    if request.method == 'POST':
        # first_name = request.form['first_name']
        # last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        con = sqlite3.connect("database.sqlite")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from user where email=? and password=?",
                    (email, password))
        data = cur.fetchone()

        if data:
            session["First_name"] = data["First_name"]
            session["Last_name"] = data["Last_name"]
            session["email"] = data["email"]
            session["password"] = data["password"]
            return redirect(url_for("back"))
        else:
            error_message = "Username and Password Mismatch"

    return render_template("back", error_message=error_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']

            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()

            # Assuming you have an auto-incrementing primary key 'id'
            cur.execute("""
                INSERT INTO user (First_name, Last_name, email, password)
                VALUES (?, ?, ?, ?)
            """, (first_name, last_name, email, password))

            con.commit()
            flash("Record Added Successfully", "success")
        except Exception as e:
            flash(f"Error in Insert Operation: {e}", "danger")
        finally:
            con.close()

            # Redirect outside of the 'finally' block to ensure the connection is closed
            return redirect("register")

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route("/back")
def back():
    return render_template("index_back.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/cv_generator")
def cv_generator():
    return render_template("cv.html")

if __name__ == '__main__':
    app.run(debug=True)

