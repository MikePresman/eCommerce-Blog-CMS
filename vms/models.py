import os
import hashlib
from vms import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from pdftickets import receipt
from flask_login import UserMixin
from vms import login, mail
from flask_mail import Message
from flask import url_for
import re
import time
from functools import wraps
from pdftickets import ticketgen
from enum import Enum


def get_current_time(time):
    time_to_return = ""
    for each in time:
        if each != ".":
            time_to_return += each
        else:
            break
    return time_to_return


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email_verification_hash = db.Column(db.String(40))
    email_verified = db.Column(db.Integer(), default=0)
    authority = db.Column(db.Integer)
    forgot_username_token = db.Column(db.String(128))
    forgot_username_stamp = db.Column(db.String(40))

    check_email_verification = False

    def send_email_authorization(self):
        msg = Message("Email Verification - Veronika's Musical Theatre",
                      sender="mikepresman@gmail.com")

        msg.html = """<body><center><img src="https://media1.tenor.com/images/f7321e08e81cb494365e418a42dfe09f/tenor.gif?itemid=8798133" align = "middle" height="200" width="200"></center><p><center><b>Thank you for signing up for VeronikaMusicTheatre.ca.</br> </br>Click Below to verify your email !</center></p></br></br>
					 <p><center><a href="http://veronikasmusicstudio.com/verify/{}">Verify Me!</a>
					 </center></p></body>""".format(self.email_verification_hash)
        msg.add_recipient(self.email)
        mail.send(msg)

    def send_reset_password_email(self):
        msg = Message("Password Reset - Veronika's Musical Theatre",
                      sender="mikepresman@gmail.com")

        msg.html = """<body><center></center><p><center></br>Click Below to reset your password for {}</center></p></br></br>
					 <p><center><a href="http://veronikasmusicstudio.com/resetpassword/{}">Password Reset!</a>
					 </center></p></body>""".format(self.username, self.forgot_username_token)
        msg.add_recipient(self.email)
        mail.send(msg)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_authority_level(current_user) -> int:
        if current_user.is_authenticated:
            user = User.query.filter_by(id=current_user.id).first()
            return user.authority
        return 0

    '''
	def admin_status(current_user_id) -> bool:
		user = User.query.filter_by(id = current_user_id).first()
		if user.authority > 0:
			return True
		return False
	'''

    def __repr__(self):
        return '<User {}>'.format(self.username)


class OneTimeLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id])

    link = db.Column(db.String(124), nullable=False)


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_link = db.Column(db.String(256))


class FailedLogins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempted_username = db.Column(db.String(64))
    ip_address = db.Column(db.String(256))
    date = db.Column(db.String(120))


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True)
    description = db.Column(db.String(120), index=True)
    image_link = db.Column(db.Text)
    content = db.Column(db.Text)
    date = db.Column(db.String(120))
    author = db.Column(db.String(32))


# one to many for users
class BlogComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    
    first_name_of_commenter = db.Column(db.String(40))
    last_name_of_commenter  = db.Column(db.String(40))
    
    date_posted = db.Column(db.String(120))
    reply = db.Column(db.Integer, default=0)

    blog_of_comment = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=True)
    blog = db.relationship("Blog", foreign_keys=[blog_of_comment])

    reply_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user_of_reply = db.relationship("User", foreign_keys=[reply_to])

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id])



class ConcertShop(db.Model):
    __tablename__ = 'concertshop'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Integer, default=0)
    concert_title = db.Column(db.String(100))
    price = db.Column(db.String(50))
    senior_price = db.Column(db.String(20))
    children_price = db.Column(db.String(20))
    quantity = db.Column(db.String(50))
    quantity_left = db.Column(db.String(50))
    description = db.Column(db.String(256))
    image_associated = db.Column(db.String(120))
    date_of_event = db.Column(db.String(120))
    time_of_event = db.Column(db.String(40))
    location = db.Column(db.String(50))

    @staticmethod
    def send_custom_email(email_addr, pdf_ticket_link, give_receipt=False, receipt_info=[]):
        with app.app_context():
            msg = Message("Veronika's Musical Theatre - Ticket",
                          sender="mikepresman@gmail.com")
            if give_receipt == False:
                msg.html = "Attached below is your ticket. Enjoy the Show !"
            else:
                msg.html = receipt.Ticket_Receipt(receipt_info)

            with open(pdf_ticket_link, encoding="utf8", errors="ignore") as fp:
                msg.attach(pdf_ticket_link, "image/jpg", fp.read())
            msg.add_recipient(email_addr)
            mail.send(msg)


class ConcertSeats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seat = db.Column(db.String(10))
    concert_name = db.Column(db.String(30))
    row = db.Column(db.String(10))
    filled = db.Column(db.Integer)

    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    date_of_purchase = db.Column(db.String(120))
    customer_email = db.Column(db.String(20))
    ticket_hash = db.Column(db.String(100))
    price_paid = db.Column(db.String(20))
    # e.g. senior, children, regular, etc used to be shown in ticket_verification
    type_of_seat_bought = db.Column(db.String(20))

    filled_by_customer_id = db.Column(
        db.Integer, db.ForeignKey('user.id'))  # returns int
    # returns vms.models.user
    customer = db.relationship("User", foreign_keys=[filled_by_customer_id])

    concert_id = db.Column(db.Integer, db.ForeignKey(
        'concertshop.id'), nullable=False)
    concert = db.relationship("ConcertShop", foreign_keys=[concert_id])

    attended = db.Column(db.Integer, default=0)
    date_attended = db.Column(db.String(20))


class ConcertReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    concert_id_associated = db.Column(db.Integer)
    seat_ids_purchased = db.Column(db.String(40))
    total_paid = db.Column(db.Integer)
    billing_name = db.Column(db.String(20))
    billing_address = db.Column(db.String(30))
    billing_city = db.Column(db.String(20))
    billing_province = db.Column(db.String(20))
    billing_postal_code = db.Column(db.String(20))
    billing_phone_number = db.Column(db.String(20))
    billing_email = db.Column(db.String(20))
    date_receipt_generated = db.Column(db.String(20))


class IndexPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    column = db.Column(db.String(64))
    picture_associated = db.Column(db.String(128))
    title_associated = db.Column(db.String(128))
    text_associated = db.Column(db.String(128))


class IndexPageUniqueImageId(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.Integer, default=1)
