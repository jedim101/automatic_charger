from flask import Flask, request

app = Flask(__name__)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    return f"""
    <h1>{code}</h1>
    """

app.run(port=3000)

