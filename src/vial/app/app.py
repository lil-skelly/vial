from flask import Flask, session, render_template

app = Flask(__name__)
app.secret_key = "SecretKey"
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

@app.route("/")
def home():
    """Displays the index page."""
    session["loggedIn"] = False
    return render_template("insecure_u.html")

@app.route("/post")
def upload_file():
    try:
        file = request.files["file"]
        filename = file.filename
        file.save("uploads/" + filename)
        response = "Upload successful"
    except Exception as e:
        response = ""
    return render_template("insecure_u.html", data=response)

if __name__ == "__main__":
    app.run(debug=True)
