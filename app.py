from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        # Handle admin login logic here
        username = request.form.get("username")
        password = request.form.get("password")
        # For now, just redirect to home (implement authentication later)
        return redirect(url_for("home"))
    return render_template("admin_login.html")

@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        # Handle user login logic here
        username = request.form.get("username")
        password = request.form.get("password")
        # For now, just redirect to home (implement authentication later)
        return redirect(url_for("home"))
    return render_template("user_login.html")

if __name__ == "__main__":
    app.run(debug=True)
