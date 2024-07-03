from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Child, CheckInOut
from forms import CheckInForm, CheckOutForm, LoginForm
from utils import check_logged_in
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

def capitalize_name(name):
    return name.capitalize()

@app.route('/check-in', methods=['GET', 'POST'])
def check_in():
    form = CheckInForm()
    if form.validate_on_submit():
        first_name = capitalize_name(form.first_name.data.strip())
        last_name = capitalize_name(form.last_name.data.strip())
        child = Child.query.filter(db.func.lower(Child.first_name) == first_name.lower(),
                                   db.func.lower(Child.last_name) == last_name.lower()).first()
        if not child:
            child = Child(first_name=first_name, last_name=last_name, checked_in=True)
            db.session.add(child)
        else:
            child.checked_in = True
            child.first_name = first_name  # Update to capitalized version
            child.last_name = last_name    # Update to capitalized version
        check_in_out = CheckInOut(child=child, action='in', timestamp=datetime.datetime.now())
        db.session.add(check_in_out)
        db.session.commit()
        flash('Välkommen, du är nu incheckad')
        resp = redirect(url_for('check_in'))
        resp.set_cookie('first_name', first_name)
        resp.set_cookie('last_name', last_name)
        return resp
    first_name = capitalize_name(request.cookies.get('first_name', ''))
    last_name = capitalize_name(request.cookies.get('last_name', ''))
    return render_template('check_in.html', form=form, first_name=first_name, last_name=last_name)


@app.route('/check-out', methods=['GET', 'POST'])
def check_out():
    first_name = capitalize_name(request.cookies.get('first_name', '').strip())
    last_name = capitalize_name(request.cookies.get('last_name', '').strip())
    if first_name and last_name:
        child = Child.query.filter(db.func.lower(Child.first_name) == first_name.lower(),
                                   db.func.lower(Child.last_name) == last_name.lower()).first()
        if child:
            if child.checked_in:
                child.checked_in = False
                child.first_name = first_name  # Update to capitalized version
                child.last_name = last_name    # Update to capitalized version
                check_in_out = CheckInOut(child=child, action='out', timestamp=datetime.datetime.now())
                db.session.add(check_in_out)
                db.session.commit()
                flash('Du är nu utcheckad')
                return redirect(url_for('check_out_message'))
            else:
                flash('Du är redan utcheckad.')
                return redirect(url_for('check_out_form'))
        else:
            flash('Ingen användare hittades.')
            return redirect(url_for('check_out_form'))
    else:
        return redirect(url_for('check_out_form'))

@app.route('/check-out-form', methods=['GET', 'POST'])
def check_out_form():
    form = CheckOutForm()
    if form.validate_on_submit():
        first_name = capitalize_name(form.first_name.data.strip())
        last_name = capitalize_name(form.last_name.data.strip())
        child = Child.query.filter(db.func.lower(Child.first_name) == first_name.lower(),
                                   db.func.lower(Child.last_name) == last_name.lower()).first()
        if child and child.checked_in:
            child.checked_in = False
            child.first_name = first_name  # Update to capitalized version
            child.last_name = last_name    # Update to capitalized version
            check_in_out = CheckInOut(child=child, action='out', timestamp=datetime.datetime.now())
            db.session.add(check_in_out)
            db.session.commit()
            flash('Du är nu utcheckad, välkommen tillbaka')
            resp = redirect(url_for('check_out_form'))
            resp.set_cookie('first_name', first_name)
            resp.set_cookie('last_name', last_name)
            return resp
    first_name = capitalize_name(request.cookies.get('first_name', ''))
    last_name = capitalize_name(request.cookies.get('last_name', ''))
    return render_template('check_out.html', form=form, first_name=first_name, last_name=last_name)

@app.route('/check-out-message')
def check_out_message():
    return render_template('check_out_message.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'password':  # simple authentication
            session['logged_in'] = True
            return redirect(url_for('organizer_view'))
        else:
            flash('Ogiltiga uppgifter')
    return render_template('login.html', form=form)

@app.route('/organizer', methods=['GET'])
@check_logged_in
def organizer_view():
    children = Child.query.all()
    return render_template('organizer_view.html', children=children)

@app.route('/history/<int:child_id>', methods=['GET'])
@check_logged_in
def history_view(child_id):
    child = Child.query.get_or_404(child_id)
    history = CheckInOut.query.filter_by(child_id=child_id).order_by(CheckInOut.timestamp.desc()).all()
    return render_template('history_view.html', child=child, history=history)

@app.route('/toggle-check/<int:child_id>', methods=['POST'])
@check_logged_in
def toggle_check(child_id):
    child = Child.query.get_or_404(child_id)
    if child.checked_in:
        child.checked_in = False
        action = 'out'
    else:
        child.checked_in = True
        action = 'in'
    check_in_out = CheckInOut(child=child, action=action, timestamp=datetime.datetime.now())
    db.session.add(check_in_out)
    db.session.commit()
    return redirect(url_for('organizer_view'))

@app.route('/remove-user/<int:child_id>', methods=['GET'])
@check_logged_in
def remove_user(child_id):
    child = Child.query.get_or_404(child_id)
    db.session.delete(child)
    db.session.commit()
    flash(f'{child.first_name} {child.last_name} har tagits bort från systemet.')
    return redirect(url_for('organizer_view'))

if __name__ == '__main__':
    app.run(debug=True)
