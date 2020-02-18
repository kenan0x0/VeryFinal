from flask import render_template, url_for, flash, redirect, request
from MFA import app, db, bcrypt
from MFA.forms import RegistrationForm, LoginForm, QRForm, SMSForm, ResetForm, ResetPWForm
from MFA.models import User
from flask_login import login_user, current_user, logout_user,login_required
import random
import qrcode
from itertools import count
from twilio.rest import Client
import smtplib, ssl


port = 587
smtp_server = "smtp.gmail.com"
sender_email = "sgtdopeaf@gmail.com"
password = "Marnk@1996"

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Verify email to be able to log in', 'success')
        receiver_email = form.email.data
        message = """\
        Subject: Confirm your email address

        Thank you for registering at our website. Please, follow this link to activate your account: http://192.168.1.7:5000/confirm/""" + receiver_email

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.confirmed_email == 1:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('qr'))
            else:
                flash('verify E-mail', 'danger')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


# Very Complicated but works xD -------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
listOfKeys = []
iid = count(-1)

@app.route("/qr", methods=['GET', 'POST'])
@login_required
def qr():
    global counter
    #Shows the form on the HTML page
    form = QRForm()

    # Create Image and save it ------
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=15,
        border=5,
    )
    numberList = []
    for i in range(6):
        randomNumber = random.randint(0,9)
        numberList.append(str(randomNumber))
    info = "".join(numberList)
    data = f"Your code is: {info}"
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("./MFA/static/pic.png")

    # Keep track of the user based on the used email, updates the key field in the Database with the generated key
    currentUser = User.query.filter_by(email=current_user.email)
    currentUser.key = info
    listOfKeys.append(currentUser.key)
    counter = next(iid)
    if form.validate_on_submit():
        enteredKey = form.key.data
        if enteredKey == listOfKeys[counter]:
            return redirect(url_for('sms'))
        else:
            return "Doesn't work"
    return render_template('qr.html', title='QR Auth', form=form)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

listOfKeys1 = []
iid1 = count(-1)
@app.route("/sms", methods=['GET', 'POST'])
@login_required
def sms():
    form = SMSForm()
    account_sid = 'AC5ce85e661bccc4b9a76a3902a3566b17'
    auth_token = 'f2f8ea8f29475f59cd2eb4f37fa696a2'
    client = Client(account_sid, auth_token)
    numberList = []
    for i in range(6):
        randomNumber = random.randint(0,9)
        numberList.append(str(randomNumber))
    info = "".join(numberList)
    print(info)
    message = client.messages \
                    .create(
                        body="Your Code is:\n" + str(info),
                        from_='+12015604591',
                        to='+31685576806'
                    )
    print(message.sid)
    currentUser = User.query.filter_by(email=current_user.email)
    currentUser.key1 = info
    listOfKeys1.append(currentUser.key1)
    counter = next(iid1)
    if form.validate_on_submit():
        enteredKey = form.key1.data
        if enteredKey == listOfKeys1[counter]:
            return "Success"
        else:
            return "Needs work"
    return render_template("sms.html", title="SMS Verification", form=form)

@app.route("/confirm/<ToBeConfirmedEmail>")
def confirm(ToBeConfirmedEmail):
    wantedEmail = ToBeConfirmedEmail
    AccountToAcctivate = User.query.filter_by(email=wantedEmail).first()
    AccountToAcctivate.confirmed_email = 1
    db.session.commit()
    flash("Your account has been successfully activated...", 'success')
    return redirect(url_for('login'))



@app.route("/reset", methods=["POST", "GET"])
def reset():
    form = ResetForm()
    if form.validate_on_submit():
        receiver_email = form.email.data
        message = """\
        Subject: Password Reset

        We're sorry to hear that your password is missing. To reset your password, please follow this link: http://192.168.1.7:5000/reset_passwd/""" + receiver_email

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            flash("A reset link has been sent to your inbox", 'success')
            return redirect(url_for('login'))
    return render_template("reset.html", title="Reset Password", form=form)


@app.route("/reset_passwd/<ToBeConfirmedEmail>", methods=["POST", "GET"])
def reset_passwd(ToBeConfirmedEmail):
    form = ResetPWForm()
    wantedEmail = ToBeConfirmedEmail
    AccountToReset = User.query.filter_by(email=wantedEmail).first()
    if form.validate_on_submit():
        newPasswd = form.passwd.data
        hashed_password = bcrypt.generate_password_hash(newPasswd).decode('utf-8')
        AccountToReset.password = hashed_password
        db.session.commit()
        flash("Your password has been reset", 'success')
        return redirect(url_for('login'))
    return render_template("reset_passwd.html", title="Reset Password", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
