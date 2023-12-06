from flask import Flask, render_template
import vertexai
from vertexai.preview.language_models import TextGenerationModel
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
key_path="./static/assets/lablabai-406919-e0c47d25bf7d.json"
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

app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index_front.html")

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

