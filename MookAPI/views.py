from MookAPI import app

@app.route("/")
def hello_world():
	"""GET Hello World! page"""

	return "Hello World, yeah!"
