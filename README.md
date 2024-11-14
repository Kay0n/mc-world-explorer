## Minecraft World Explorer

Minecraft World Explorer is a simple Flask web interface designed to quickly spin up multiple vanilla Minecraft worlds as on a server for exploration.


### Setup

Clone or download the repository to your local machine

Place your Minecraft worlds in vanilla format in the /saves directory
- Each world should be named in the format: `<world_name>-<version>`, for example: `fav-world-1.20.4`

The program relies on a .env file in the root directory for sensitive settings
Add the following variables to your .env file:
- SESSION_SECRET_KEY: A secret key used to sign the session cookie for user authentication
- AUTH_PASSWORD: The password required to access the admin page

Example .env file:
```
SESSION_SECRET_KEY=my_secret_key
AUTH_PASSWORD=my_admin_password
WEB_PORT=5000
```


### Installation

Install the required Python packages by running:

`pip install -r requirements.txt`

### Usage

Start the application by running:

`python src/main.py`

Access the web interface through your browser at `http://localhost:<WEB_PORT>` (specified in .env)
Use the specified admin password to start the server. Configure any server-specific settings in the `/server` dir