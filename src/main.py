from flask import Flask, render_template, session
import os
from mc_server import MinecraftServer
from save_manager import SaveManager
from routes import auth, server, worlds
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(__file__)) # a directory above this file's dir
SAVES_DIR = os.path.join(BASE_DIR, "saves")
SERVER_JARS_DIR = os.path.join(BASE_DIR, "server-jars")
SERVER_DIR = os.path.join(BASE_DIR, "server")


load_dotenv(BASE_DIR)


os.makedirs(SAVES_DIR, exist_ok=True)
os.makedirs(SERVER_JARS_DIR, exist_ok=True)
os.makedirs(SERVER_DIR, exist_ok=True)


app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET_KEY")
save_manager = SaveManager(SAVES_DIR)


# allow blueprints to access config options 
app.config['SAVE_MANAGER'] = save_manager
app.config["MC_SERVER"] = MinecraftServer(SERVER_DIR, SERVER_JARS_DIR, save_manager)
app.config["AUTH_PASSWORD"] = os.getenv("AUTH_PASSWORD") 


# avoid conflicts with vue templating
app.jinja_env.block_start_string = '<%'
app.jinja_env.block_end_string = '%>'
app.jinja_env.variable_start_string = '%%'
app.jinja_env.variable_end_string = '%%'
app.jinja_env.comment_start_string = '<#'
app.jinja_env.comment_end_string = '#>'


app.register_blueprint(auth.blueprint)
app.register_blueprint(server.blueprint)
app.register_blueprint(worlds.blueprint)


@app.route('/')
def index():
    if session.get('logged_in'):
        return render_template('admin.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)