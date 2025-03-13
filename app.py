import os
from flask import jsonify, Flask, request, render_template
from flask_cors import CORS

from azure.identity import CertificateCredential
from openai import AzureOpenAI

app = Flask(__name__)
CORS(app)

if os.environ["no_proxy"].split(",")[-1] != "openai.azure.com":
    os.environ["no_proxy"]=os.environ["no_proxy"]+",openai.azure.com"

os.environ["http_proxy"] = "HTTP_PROXY_ADDRESS"
os.environ["https_proxy"] = "HTTPS_PROXY_ADDRESS"

# Azure OpenAI credential settings - Please fill in with actual credentials in private environment
# CONFIG_SECTION: AUTH_CREDENTIALS
client_id = "CLIENT_ID"
certificate_path = "CERTIFICATE_PATH"
tenant_id = "TENANT_ID"
model = "MODEL_NAME"
azure_endpoint = "AZURE_ENDPOINT"

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
    client = AzureOpenAI(
        api_key=get_token(),
        api_version="2024-02-15-preview",
        azure_endpoint=azure_endpoint
    )
    return client


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
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
