from flask import render_template, redirect, url_for, request, session, current_app, Blueprint


blueprint = Blueprint("auth", __name__)



@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == current_app.config["AUTH_PASSWORD"]:
            session['logged_in'] = True
            return redirect(url_for("index"))
        return render_template('login.html', error='Invalid password')
    else:
        return render_template('login.html')



@blueprint.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))