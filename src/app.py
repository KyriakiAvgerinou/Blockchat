from flask import Flask
from endpoints import blockchat_bp

app = Flask(__name__) # initialize the application
app.register_blueprint(blockchat_bp, url_prefix = "/blockchat") # register blockchat_bp blueprint

if __name__ == "__main__":
    app.run(debug = True)