# wsgi.py
import email


from flask import Flask, render_template , request
from flask_mail import Mail, Message


app = Flask(__name__)


# Mail configuration (example for Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vikkikumar9694@gmail.com'   # admin email
app.config['MAIL_PASSWORD'] = 'ooby frzc laqi rfqy'  
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        
        name = request.form.get('name')
        email = request.form.get('email')
        service = request.form.get('service')
        message = request.form.get('message')

         # Email बनाना
        msg = Message(subject="New Contact Form Submission",
                  sender=app.config['MAIL_USERNAME'],   # हमेशा आपका Gmail
                  recipients=['vikkikumar9694@gmail.com'])  # Admin का email

        msg.body = f"""
        📩 New Contact Form Submission:

        Name: {name}
        Email: {email}
        Service: {service}
        Message: {message}
        """

        # User का email reply-to में डालें
        msg.reply_to = email

        # Email भेजना
        mail.send(msg)

        return render_template('thank_you.html', success=True)
    return render_template('contact.html')


if __name__ == '__main__':
    app.run
