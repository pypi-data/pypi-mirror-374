from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/hola")
def hola():
    return "Hola CloudShell!!!!", 200

@app.get("/")
def root():
    return jsonify(status="ok", hint="GET /hola"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
