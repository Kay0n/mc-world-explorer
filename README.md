
## Minecraft World Explorer

A simple flask web interface to quickly spin up a large number of vanilla minecraft worlds 
into quick servers for exploration. 


### Setup

Place worlds in vanilla format in the `/saves` directory.
They should be named `<world_name>-<version>` e.g. `fav-world-1.20.4`

The program looks for a `.env` file in the root directory.
 - `SESSION_SECRET_KEY` - Secret key used to sign the session cookie when logged in
 - `AUTH_PASSWORD` - Password for admin page 

### Usage

Install python packages using `pip install -r requirements.txt`

Run using `python main.py`