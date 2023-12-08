from flask import Flask, render_template,request, redirect, url_for, session,flash
import re
import sqlite3
import base64
from werkzeug.utils import secure_filename
import tempfile
import openai
import uuid
import os
import config
import db
from flask import Flask, render_template, request, jsonify
import vertexai
from vertexai.preview.language_models import ChatModel
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.cloud import aiplatform
from trulens_eval import TruChain, Feedback, Tru, LiteLLM
from langchain.chains import LLMChain
from langchain.llms import VertexAI
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from datetime import datetime
import base64
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
database_file = "database.json"
database = db.load(database_file)
settings = config.load("settings.json")
class InfoUser:
    def __init__(self):
        self.Title = ""
        self.Phone = ""
        self.Profile = ""
        self.Address = ""
        self.Linkedin = ""
        self.Skills = ""
        self.Languages = ""
        self.Education = ""
        self.PE = ""
        self.Interests = ""
        self.Certificates = ""
        self.Organizations = ""
        self.Photo = ""
tru = Tru()
key_path = "lablabai-406919-e0c47d25bf7d.json"
credentials = Credentials.from_service_account_file(key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"])

if credentials.expired:
    credentials.refresh(Request())
PROJECT_ID = os.environ.get('GCP_PROJECT') #Your Google Cloud Project ID
LOCATION = os.environ.get('GCP_REGION')   #Your Google Cloud Project Region
aiplatform.init(project = PROJECT_ID,location=LOCATION, credentials=credentials)

full_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template=
        "Provide a helpful response with relevant background information for the following: {prompt}",
        input_variables=["prompt"],
    )
)

chat_prompt_template = ChatPromptTemplate.from_messages([full_prompt])

llm = VertexAI()

chain = LLMChain(llm=llm, prompt=chat_prompt_template, verbose=True)
litellm = LiteLLM(model_engine="chat-bison")
relevance = Feedback(litellm.relevance_with_cot_reasons).on_input_output()
f2=Feedback(litellm.criminality_with_cot_reasons).on_output()
f3=Feedback(litellm.correctness_with_cot_reasons).on_output()
f4=Feedback(litellm.sentiment_with_cot_reasons).on_output()
f5=Feedback(litellm.insensitivity).on_output()
tru_recorder = TruChain(chain,app_id='Chain_ChatApplication',feedbacks=[relevance,f2,f3,f4,f5])


# display(llm_response)
tru.get_records_and_feedback(app_ids=[])[0] # pass an empty list of app_ids to get all
tru.run_dashboard() # open a local streamlit app to explore
# from pdfminer.high_level import extract_pages, extract_text
# import vertexai
# from vertexai.preview.language_models import TextGenerationModel
# from google.auth.transport.requests import Request
# from google.oauth2.service_account import Credentials
# from trulens_eval import TruChain, Feedback, Huggingface, Tru ,OpenAI
# key_path="lablabai-406919-e0c47d25bf7d.json"
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
# hugs = Huggingface()
# openai = OpenAI()
# tru = Tru()
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
app.config['TESTING'] = True
app.testing = True
app.secret_key="123"

def catch_id():
    con = sqlite3.connect("database.sqlite")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT id FROM user WHERE email=?", (session['email'],))
    data = cur.fetchone()

    if data:
        user_id = data["id"]
        return user_id
    else:
        error_message = "User not found"

    # Handle the case where no user is found appropriately.
    # Here, I'll raise an exception for demonstration purposes.
    raise ValueError("User not found")
def get_info():
    info_user = InfoUser()
    user_id = catch_id()
    con = sqlite3.connect("database.sqlite")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM info WHERE user_id=?", (user_id,))
    data = cur.fetchone()
    if data:
        info_user.Title = data["title"]
        info_user.Phone = data["phone_number"]
        info_user.Profile = data["profile"]
        info_user.Address = data["address"]
        info_user.Linkedin = data["linkedin_profile"]
        info_user.Skills = data["skills"]
        info_user.Languages = data["languages"]
        info_user.Education = data["education"]
        info_user.PE = data["professional_experience"]
        info_user.Interests = data["interests"]
        info_user.Certificates = data["certificates"]
        info_user.Organizations = data["organizations"]
        # info_user.Photo = data["photo"]
        photo_blob = data["Photo"]
        if photo_blob:
            # Convert the blob data to base64
            photo_base64 = base64.b64encode(photo_blob).decode('utf-8')
            info_user.Photo = f"data:image/jpeg;base64,{photo_base64}"
        else:
            info_user.Photo = None
        return info_user
    else:
        return None
    
@app.route("/")
def home():
    return render_template("index_front.html")
@app.route("/editprofile", methods=['GET', 'POST'])
def editprofile():
    con = None  # Initialize con outside the try block
    info_user = InfoUser()
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
                            UPDATE info
                            SET phone_number=?, linkedin_profile=?, title=?, photo=?, address=?, skills=?, languages=?, profile=?, education=?, professional_experience=?, interests=?, certificates=?, organizations=?
                            WHERE user_id=?
                        """, (phone_number, linkedin_p, title, photo_binary, address, skills, languages, profile, education, professional_experience, interests, certificates, organizations, user_id))
                       
                        con.commit()
                        
                        info_user=get_info()
                        print(info_user.Title)
                        print(info_user.Photo)
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
                if(not info_user.Photo):
                    info_user.Photo="../static/Back/assets/img/user.jpg"

                return render_template('editprofile.html',info_user=info_user)
    if(not info_user.Photo):
        info_user.Photo="../static/Back/assets/img/user.jpg"
    return render_template('editprofile.html',info_user=info_user)

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
            return render_template('register.html',error_message=error_message)

    return render_template("back", error_message=error_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            print("try")
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']

            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()
            print("hhhhhhhhh")
            # Assuming you have an auto-incrementing primary key 'id'
            cur.execute("""
                INSERT INTO user (First_name, Last_name, email, password)
                VALUES (?, ?, ?, ?)
            """, (first_name, last_name, email, password))
            print("baad cur")
            user_id = cur.lastrowid
            print(user_id)
            cur.execute("""
                INSERT INTO info (user_id)
                VALUES (?)
            """, (user_id,))
            print("baad cur 2")
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
    info_user = InfoUser()
    info_user=get_info()
    if(not info_user.Photo):
        info_user.Photo="../static/Back/assets/img/user.jpg"
    return render_template("index_back.html",u=info_user)

@app.route("/form", methods=["POST"])
def form():
    Title=request.form["Title"]
    Phone=request.form["Phone"]
    Profile=request.form["Profile"]
    Email=request.form["Email"]
    Address=request.form["Address"]
    Linkedin=request.form["Linkedin"]
    Skills=request.form["Skills"]
    Languages=request.form["Languages"]
    Education=request.form["Education"]
    PEE=request.form["PE"]
    Interests=request.form["Interests"]
    Certificates=request.form["Certificates"]
    Organizations=request.form["Organizations"]
    return render_template("form.html",Title=Title,Phone=Phone,Profile=Profile,Email=Email,Address=Address,Linkedin=Linkedin,Skills=Skills,Languages=Languages,Education=Education,PE=PEE,Interests=Interests,Certificates=Certificates,Organizations=Organizations)


@app.route("/cv_generator")
def cv_generator():
    info_user = InfoUser()
    info_user=get_info()
    return render_template("cv.html",info_user=info_user)

@app.route("/chat/")
def index():
    info_user = InfoUser()
    info_user=get_info()
    return render_template("test.html",info_user=info_user)

@app.route("/new_chat", methods=["POST"])
def new_chat():
    chat_id = str(uuid.uuid4())

    thread = openai.beta.threads.create()
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%a.%m/%Y at %H:%M")
    chat = {
        "id": chat_id,
        "thread_id": thread.id,
        "title": formatted_datetime,
    }

    database["conversations"][chat_id] = chat
    db.save(database_file, database)

    return render_template(
        "chat_button.html",
        chat=chat
    )

@app.route("/load_chat/<chat_id>")
def load_chat(chat_id):
    thread_id = database["conversations"][chat_id]["thread_id"]

    messages = openai.beta.threads.messages.list(
        thread_id=thread_id,
        order="desc",
    )

    message_list = []

    for message in messages.data:
        message_list.append({
            "role": message.role,
            "content": message.content[0].text.value
        })

    message_list = reversed(message_list)

    return render_template(
        "messages.html",
        messages=message_list,
        chat_id=chat_id
    )

@app.route("/conversations")
def conversations():
    chats = database["conversations"].values()
    return render_template("conversations.html", conversations=chats)

@app.route("/send_message", methods=["POST"])
def send_message():
    chat_id = request.form["chat_id"]
    file_ids = []

    if "file" in request.files:
        file = request.files["file"]
        if file.filename != "":
            temp_dir = tempfile.mkdtemp()

            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, filename)

            print(f"Saving to {file_path}")

            file.save(file_path)
            uploaded_file = openai.files.create(
                file=openai.file_from_path(file_path),
                purpose="assistants",
            )

            file_ids.append(uploaded_file.id)

            os.remove(file_path)
            os.rmdir(temp_dir)

    message = {
        "role": "user",
        "content": request.form["message"]
    }

    chat = database["conversations"][chat_id]

    openai.beta.threads.messages.create(
        thread_id=chat["thread_id"],
        role=message["role"],
        content=message["content"],
        file_ids=file_ids,
    )

    return render_template(
        "user_message.html",
        chat_id=chat_id,
        message=message
    )

@app.route("/get_response/<chat_id>")
def get_response(chat_id):
    chat = database["conversations"][chat_id]

    run = openai.beta.threads.runs.create(
        thread_id=chat["thread_id"],
        assistant_id=settings["assistant_id"],
    )

    while True:
        run = openai.beta.threads.runs.retrieve(
            run_id=run.id,
            thread_id=chat["thread_id"]
        )

        if run.status not in ["queued", "in_progress", "cancelling"]:
            break

    messages = openai.beta.threads.messages.list(
        thread_id=chat["thread_id"],
        order="desc",
        limit=1,
    )

    message = {
        "role": "assistant",
        "content": messages.data[0].content[0].text.value
    }

    return render_template(
        "assistant_message.html",
        message=message
    )

@app.route('/chat2')
def chat():
    ###
    return render_template('chat2.html')

@app.route('/palm2', methods=['GET', 'POST'])
def vertex_palm_chat():
    user_input = ""
    if request.method == 'GET':
        user_input = request.args.get('user_input')

    else:
        user_input = request.form['user_input']
    # chat_model = create_session()
    with tru_recorder as recording:
        llm_response = chain(user_input)
        text_value = llm_response['text']

    # content = response(recording,user_input)
    return jsonify(content=text_value)
# Function to check if the file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}
full_prompt2 = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template="Provide a helpful response that gives the strengths and weaknesses to improve this resume: {prompt}",
        input_variables=["prompt"],
    )
)
chat_prompt_template2 = ChatPromptTemplate.from_messages([full_prompt2])
chain2 = LLMChain(llm=llm, prompt=chat_prompt_template2, verbose=True)
litellm = LiteLLM(model_engine="chat-bison")
relevance = Feedback(litellm.relevance_with_cot_reasons).on_input_output()
f2=Feedback(litellm.criminality_with_cot_reasons).on_output()
f3=Feedback(litellm.correctness_with_cot_reasons).on_output()
f4=Feedback(litellm.sentiment_with_cot_reasons).on_output()
f5=Feedback(litellm.insensitivity).on_output()
f6=Feedback(litellm.coherence).on_output()
tru_recorder2 = TruChain(chain2, app_id='Chain_strength_and_weaknesses ', feedbacks=[relevance,f2,f3,f4,f5,f6])
tru.run_dashboard() # open a local streamlit app to explore

@app.route('/doc')
def doc():
    return render_template('doc.html')

@app.route('/palm2doc', methods=['POST'])
def vertex_palmdoc():
    if 'file' not in request.files:
        return render_template('doc.html', error="No file provided")

    file = request.files['file']

    if file.filename == '':
        return render_template('doc.html', error="No selected file")

    if file and allowed_file(file.filename):
        # Extract text from the PDF using PdfReader
        reader = PdfReader(file)
        pdf_text = ""
        for page_number, page in enumerate(reader.pages):
            pdf_text += page.extract_text()

        # Process text with the PaLM API
        with tru_recorder2 as recording:
            llm_response = chain2(pdf_text)
            strengths_weaknesses = llm_response['text']
            # Assuming strengths_weaknesses is a string containing both strengths and weaknesses
            # and starts with "**Strengths:**" and "**Weaknesses:**"
            start_strengths = "**Strengths:**"
            start_weaknesses = "**Weaknesses:**"

            # Find the starting index of strengths and weaknesses
            index_strengths = strengths_weaknesses.find(start_strengths)
            index_weaknesses = strengths_weaknesses.find(start_weaknesses)

            # Check if both markers are present
            if index_strengths != -1 and index_weaknesses != -1:
                # Extract strengths and weaknesses based on the markers
                strengths = strengths_weaknesses[index_strengths + len(start_strengths):index_weaknesses].strip()
                weaknesses = strengths_weaknesses[index_weaknesses + len(start_weaknesses):].strip()

                # Split strengths and weaknesses into lists, filtering out empty items
                strengths_list = [s.strip() for s in strengths.split('-') if s.strip()]
                weaknesses_list = [w.strip() for w in weaknesses.split('-') if w.strip()]
            else:
                # Handle the case where markers are not found
                strengths_list = []
                weaknesses_list = []

            # Now strengths and weaknesses should contain the desired text

                print(strengths_list)
                print(weaknesses_list)
        return render_template('doc.html', strengths=strengths_list, weaknesses=weaknesses_list)

    return render_template('doc.html', error="Invalid file type")

@app.route('/button')
def button():
    return render_template('button.html')
@app.route('/specific_cv',  methods=['GET', 'POST'])
def specific_cv():
    info_user = InfoUser()
    info_user=get_info()    
    assistant_response_template = """
    you are a career coach . i'm applying  for this role:

    Job Description: {job_description}

    below is the experience section for my resume. rephrase my experiences to showcase my relevant skills for this role and organize information in a way that's easy to read. include keywords that are specific to the job description and industry :

    Skills:{skills}
    Professional Experience:{professional_experience}

    Please use this format for the output :

    Experience Title - role:

    - [bullet point one for experience]
    - [bullet point two for experience
    - [bullet point three for experience]
    """
    u_input = request.form['u_input']
    if request.method == 'POST':
        user_input = {
            "job_description": u_input,
            "professional_experience": info_user.PE,
            "skills":info_user.Skills
        }
        
        # Construct the assistant's response using the template
        assistant_prompt = assistant_response_template.format(**user_input)
        with tru_recorder as recording:
            llm_response = chain(assistant_prompt)
            text_value = llm_response['text']
        # Define the markers for job title, role, and skills
            # Define the markers for job title, role, and skills
# Define the markers for job title, role, and skills
        print(text_value)   
        start_job_title = "**"
        end_job_title = "**"
        start_role = "** -"
        start_skills = "Key Skills:"

        # Find the starting and ending index of job title
        index_job_title_start = text_value.find(start_job_title)
        index_job_title_end = text_value.find(end_job_title, index_job_title_start + len(start_job_title))

        # Find the starting index of role
        index_role = text_value.find(start_role, index_job_title_end)

        # Find the starting index of skills
        index_skills = text_value.find(start_skills)

        # Extract job title, role, and skills based on the markers
        job_title = text_value[index_job_title_start + len(start_job_title):index_job_title_end].strip()
        role_raw = text_value[index_job_title_end + len(end_job_title):index_role].strip()
        skills_raw = text_value[index_skills + len(start_skills):].strip()

        # Split role into a list of bullet points
        role_list = [role.strip() for role in role_raw.split('.') if role.strip()]

        # Split skills into a list, filtering out empty items
        skills_list = [s.strip() for s in skills_raw.split('-') if s.strip()]
        # print()
        # # Output the extracted job title, role, and skills
        # print("Job Title:", job_title)
        # print("Role:", role_list)
        # print("Skills:", skills_list)
    # content = response(recording,user_input)
    return render_template('cv.html',info_user=info_user ,message_gpt=text_value,role_list=role_list,job_title=job_title)


if __name__ == '__main__':
    app.run(debug=True)

