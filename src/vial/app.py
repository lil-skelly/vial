from flask import Flask, session, render_template_string

app = Flask(__name__)
app.secret_key = "SecretKey"


@app.route("/")
def index():
    """Displays the index page."""

    session["loggedIn"] = False
    return render_template_string(
        """
<h1>Hello World</h1>
        """
    )


if __name__ == "__main__":
    app.run(debug=True)
