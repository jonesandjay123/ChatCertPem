import os
import base64
import uuid
import imghdr
from werkzeug.utils import secure_filename

from flask import jsonify, Flask, request, render_template
from flask_cors import CORS
import requests

from azure.identity import CertificateCredential
from azure.core.credentials import AccessToken
from openai import AzureOpenAI

app = Flask(__name__)
CORS(app)

# Proxy settings - Please fill in with actual proxy settings in private environment
# CONFIG_SECTION: PROXY_SETTINGS
os.environ["http_proxy"] = "YOUR_HTTP_PROXY"
os.environ["https_proxy"] = "YOUR_HTTPS_PROXY"

# Azure OpenAI credential settings - Please fill in with actual credentials in private environment
# CONFIG_SECTION: AUTH_CREDENTIALS
client_id = "YOUR_CLIENT_ID"
certificate_path = "YOUR_CERTIFICATE_PATH"
tenant_id = "YOUR_TENANT_ID"
model = "YOUR_MODEL_NAME"

# Image processing settings
UPLOAD_FOLDER = "temp_uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """
    Check if the file has an allowed extension
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image(file_path):
    """
    Validate that the file is actually an image
    """
    img_type = imghdr.what(file_path)
    if img_type is None or img_type.lower() not in ALLOWED_EXTENSIONS:
        return False
    return True


def get_token():
    """
    Get authentication token from Azure using certificate credentials
    """
    scope = "https://cognitiveservices.azure.com/.default"
    credential = CertificateCredential(
        client_id=client_id,
        certificate_path=certificate_path,
        tenant_id=tenant_id,
        scope=scope
    )
    cred_info = credential.get_token(scope)
    token = cred_info.token
    return token


def get_openai_instance():
    """
    Create and return an Azure OpenAI client instance
    """
    # CONFIG_SECTION: AZURE_ENDPOINT
    client = AzureOpenAI(
        credential=get_token(),
        api_version="2024-02-15-preview",
        azure_endpoint="YOUR_AZURE_ENDPOINT"
    )
    return client


def encode_image(image_path):
    """
    Encode image file to base64 string
    """
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image


def process_image_and_question(image_path, question):
    """
    Process an image and a question using Azure OpenAI
    """
    # Validate image before processing
    if not validate_image(image_path):
        raise ValueError("Invalid image file")

    encoded_image = encode_image(image_path)

    # Prepare the conversation history
    conversation_history = [
        {
            "role": "system",
            "content": "You are an image recognition analysis who analyzes images to help answer user questions. In your response, always provide the conclusion/summary first, followed by detailed analysis. Refrain from showing '###' and '***' in the response. Focus your analysis on the content of the images provided and ensure your insights are based solely on the visual data available."
        },
        {
            "role": "user",
            "content": question
        },
        {
            "role": "user",
            "content": f"data:image/jpeg;base64,{encoded_image}"
        }
    ]

    # Get the OpenAI client
    client = get_openai_instance()

    # Call the OpenAI API
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=conversation_history
    )

    # Extract the assistant's response
    assistant_response = response.choices[0].message.content
    return {"answer": assistant_response}


@app.route("/process", methods=["POST"])
def process_endpoint():
    """
    Process image analysis request
    """
    if "question" not in request.form:
        return jsonify({"error": "Missing question"}), 400
    
    if "image" not in request.files:
        return jsonify({"error": "Missing image file"}), 400

    question = request.form["question"]
    image_file = request.files["image"]

    # Validate file presence and format
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(image_file.filename):
        return jsonify({"error": "File format not allowed"}), 400

    # Create a secure filename with UUID to prevent collisions
    filename = secure_filename(image_file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        # Save the image to a temporary location
        image_file.save(image_path)
        
        # Check if file is truly an image
        if not validate_image(image_path):
            os.remove(image_path)
            return jsonify({"error": "Invalid image file"}), 400

        # Process the image
        result = process_image_and_question(image_path, question)
        print(f"Answer: {result['answer']}")
        return jsonify(result)
    
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Clean up: delete temporary file
        if os.path.exists(image_path):
            os.remove(image_path)


@app.route("/")
def index():
    """
    Render the main chat interface
    """
    return render_template("index.html")


def process_chat(question):
    """
    Process text chat request
    """
    # Prepare conversation history
    conversation_history = [
        {
            "role": "system",
            "content": "You are a helpful assistant who can answer various questions. Please provide useful, safe, and ethical responses."
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # Get OpenAI client
    client = get_openai_instance()

    # Call OpenAI API
    response = client.chat.completions.create(
        model=model,
        temperature=0.7,
        messages=conversation_history
    )

    # Extract assistant's response
    assistant_response = response.choices[0].message.content
    return {"answer": assistant_response}


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """
    Process chat message and return response
    """
    data = request.json
    if "question" not in data:
        return jsonify({"error": "Missing question content"}), 400

    question = data["question"]

    try:
        result = process_chat(question)
        print(f"Answer: {result['answer']}")
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify(result)


if __name__ == "__main__":
    print("---This Flask app is starting with the latest code version---")
    app.run(host="0.0.0.0", port=5000, debug=True)
