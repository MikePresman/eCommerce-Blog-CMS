from vms import app, db, mail, celery
from flask_mail import Message
from vms.decorators import admin_only, login_necessary
from vms.models import User, FailedLogins, Gallery, Blog, ConcertShop, ConcertSeats, ConcertReceipt, IndexPage, IndexPageUniqueImageId, BlogComment, get_current_time
from vms.forms import LoginForm, RegistrationForm, GalleryForm, StorePageForm, ForgotCred, ResetPasswordForm, ChangeEmailForm
from config import Config
from datetime import datetime
from flask import render_template, redirect, flash, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from pdftickets import ticketgen, receipt
from werkzeug.utils import secure_filename
import os
import hashlib
import qrcode
import json
import stripe
import urllib.request
import time
import logging

pub_key = 'pk_test_tsGJ0qQX3aez4xB1v5tdFnZA00XwTP7RUQ'
secret_key = 'sk_test_wnDZsbX8xHhWVFpifoXFHr2G00lbe5VZgH'
stripe.api_key = secret_key

@app.route("/user_purchases/<user_id>", methods=["GET"])
@admin_only(current_user)
def user_purchases(user_id):
    
    receipts_for_user = ConcertReceipt.query.filter_by(
        user_id=int(user_id)).all()

    individual_receipts = {}
    

    # this is figuring out seating details
    for each_receipt in receipts_for_user:
        if "," in each_receipt.seat_ids_purchased:
            seat_ids_for_that_receipt = each_receipt.seat_ids_purchased.split(
                ",")
        else:
            seat_ids_for_that_receipt = [each_receipt.seat_ids_purchased]

        for seat in seat_ids_for_that_receipt:
            seat_details = ConcertSeats.query.filter_by(id=int(seat)).first()
            if seat_details is None: #this is a check if the concertseats row was deleted after the ticket was purchased
                seat_info = ['deleted seat', 'deleted seat']
                print(seat)
            else:
                seat_info = [seat_details.row, seat_details.seat]
            if each_receipt not in individual_receipts:
                individual_receipts[each_receipt] = [seat_info]
            else:
                individual_receipts[each_receipt].append(seat_info)
    
    return render_template("receipts_for_user.html", receipts_info=individual_receipts)


@app.route("/receipts-for-event/<concert_id>/", methods=["POST", "GET"])
def receipts_for_event(concert_id):
    receipts_for_concert = ConcertReceipt.query.filter_by(
        concert_id_associated=int(concert_id)).all()
    receipt_info_with_names = []

    for each in receipts_for_concert:
        # get the seat_ids that they bought
        if "," in each.seat_ids_purchased:
            seats = each.seat_ids_purchased.split(",")
        else:
            seats = [each.seat_ids_purchased]
        seating_info = []
        for seat in seats:
            seat_details = ConcertSeats.query.filter_by(id=int(seat)).first()
            seating_info.append([seat_details.row, seat_details.seat])

        user = User.query.filter_by(id=each.user_id).first()
        receipt_info_with_names.append([user, each, seating_info])

    return render_template("receipts_for_concert.html", receipts_info=receipt_info_with_names)


@app.route("/myaccount", methods=["GET", "POST"])
def my_account():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if request.method == "POST" and request.form.get('email') is not None:
            user.send_email_authorization()
            flash("Check your spam folder for the email")
            return redirect(url_for('index'))
        if user.email_verified == 0:
            return render_template("myaccount.html", user=user.username, verified=0)
        else:
            return render_template("myaccount.html", user=user.username, verified=1)
    else:
        return redirect("login")


@app.route("/changepassword", methods=["POST", "GET"])
def change_password():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        form = ResetPasswordForm()
    
        if request.method == "POST" and form.new_password.data is not None:
            user.set_password(form.new_password.data)
            db.session.commit()
            logout_user()
            return redirect("login")
        
        return render_template("changepassword.html", form=form)
    else:
        return redirect("login")


@app.route("/changeemail", methods=["POST", "GET"])
def change_email():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        form = ChangeEmailForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.new_email.data).first()
            if user is None:
                user = User.query.filter_by(id=current_user.id).first()
                user.email = form.new_email.data
                user.email_verified = 0
                user.send_email_authorization()
                flash("Check your spam folder your authorization email")
                db.session.commit()
                return redirect("myaccount")
            else:
                flash("Email already taken")
                return redirect("changeemail")
        return render_template("changeemail.html", form=form)
    else:
        return redirect("login")


@app.route("/mytickets", methods=["POST", "GET"])
def my_tickets():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user.email_verified == 0:
            flash("Please verify your email first")
            return redirect("myaccount")
        if request.method == "POST":
            concert = ConcertSeats.query.filter_by(concert_id=request.form.get(
                'concert_id')).filter_by(filled_by_customer_id=current_user.id).all()
            concertshop = ConcertShop.query.filter_by(
                id=request.form.get('concert_id')).first()
            user = User.query.filter_by(id=current_user.id).first()
            email = user.email
            ticket_info = []
            image_names = []

            for each in concert:
                qr_code_hash = hashlib.md5(os.urandom(32)).hexdigest()
                qr_image_name = 'pdftickets/qrcode' + qr_code_hash + ".jpg"
                img = qrcode.make(request.url_root +
                                  'ticket_verification' + '/' + qr_code_hash)
                img.save(qr_image_name)
                image_names.append(qr_image_name)
                ticket_info.append([each.first_name, each.last_name, each.concert_name, concertshop.date_of_event, each.row,
                                    each.seat, concertshop.location, qr_image_name, concertshop.image_associated, each.type_of_seat_bought])
            
            send_email.delay(ticket_info, email, images_to_delete = image_names)
            
            flash("Check your spam folder for the tickets email")
            return redirect(url_for('my_account'))

        user = User.query.filter_by(id=current_user.id).first()
        concert_seats = ConcertSeats.query.filter_by(customer=user).all()
        concerts_paid_for_with_seats = {}
        for each in concert_seats:
            if each.concert_id in concerts_paid_for_with_seats:
                continue
            else:

                concert = ConcertShop.query.filter_by(
                    id=each.concert_id).first()
                concerts_paid_for_with_seats[each.concert_id] = [
                    concert.image_associated, concert.concert_title]
        return render_template("mytickets.html", tickets=concerts_paid_for_with_seats)
    return redirect('login')


@app.route("/index", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def index():
    record = IndexPage.query.filter_by(column="top").first()
    left_column = IndexPage.query.filter_by(column="left").first()
    middle_column = IndexPage.query.filter_by(column="middle").first()
    right_column = IndexPage.query.filter_by(column="right").first()
    return render_template("index.html", user_info=current_user, top=record, left=left_column, middle=middle_column, right=right_column, user_authority_level=User.get_authority_level(current_user))


@app.route("/index_editor", methods=["GET", "POST"])
def index_editor():
    if request.method == "POST" and request.form.get("index-title") is not None or request.files.get('image') is not None or request.form.get("index-text") is not None:
        index_title = request.form.get("index-title")
        index_picture = request.files.get('image')
        index_text = request.form.get("index-text")

        if request.form.get("call_from") == "Index Upload:Top":
            record = IndexPage.query.filter_by(column="top").first()
            column = "top"
        elif request.form.get("call_from") == "Index Upload:Left":
            record = IndexPage.query.filter_by(column="left").first()
            column = "left"
        elif request.form.get("call_from") == "Index Upload:Middle":
            record = IndexPage.query.filter_by(column="middle").first()
            column = "middle"
        elif request.form.get("call_from") == "Index Upload:Right":
            record = IndexPage.query.filter_by(column="Right").first()
            column = "right"

        if record is not None and request.files.get("image") is None:
            record.title_associated = index_title
            record.text_associated = index_text
        # this is done because the page doesnt load in with the image inside the span class like it does for the text fields
        elif record is not None and request.files.get("image") is not None:
            record.title_associated = index_title
            record.text_associated = index_text
            upload_image(request.files["image"], request.form.get("call_from"))
        elif record is None and request.files.get("image") is None:
            record = IndexPage(
                column=column, title_associated=index_title, text_associated=index_text)
            db.session.add(record)
        elif record is None and request.files.get("image") is not None:
            record = IndexPage(
                column=column, title_associated=index_title, text_associated=index_text)
            upload_image(request.files["image"], request.form.get("call_from"))
        db.session.commit()
        return redirect(url_for('index_editor'))

    record = IndexPage.query.filter_by(column="top").first()
    left_column = IndexPage.query.filter_by(column="left").first()
    middle_column = IndexPage.query.filter_by(column="middle").first()
    right_column = IndexPage.query.filter_by(column="right").first()
    return render_template("index_editor.html", top=record, left=left_column, middle=middle_column, right=right_column)

# bug occurs when no tickets left in list
@app.route("/generate-custom-ticket", methods=["GET", "POST"])
def generate_custom_ticket():
    ticket_details = request.form.get("ticket-info")
    ticket_queue = request.form.get("ticket-queue")
    submit_queue = request.form.get("submit-queue")
    clear_queue = request.form.get("clear-queue")
    delete_individual_from_queue = request.form.get("queue-delete-individual")

    if delete_individual_from_queue is not None and 'queue' in session:
        individual_info = delete_individual_from_queue.split(":")
        queue = json.loads(session['queue'])
        for index, each in enumerate(queue):
            if each[9] == individual_info[0] and each[4] == individual_info[1] and each[5] == individual_info[2]:
                del(queue[index])
        session['queue'] = json.dumps(qeuue)

    # Clear queue to start fresh
    if request.method == "POST" and clear_queue is not None:
        session.pop('queue')
        return redirect(url_for("generate_custom_ticket"))

    # Adding tickets to queue
    if request.method == "POST" and ticket_queue is not None:
        try:
            ticket_details = request.form.get("ticket-info").split(",")
        except Exception as e:
            flash(e)
            return redirect(url_for('generate_custom_ticket'))
        else:
            row = ticket_details[0][2:-1]
            seat = ticket_details[1][2:-1]
            concert_id = ticket_details[2][1:-1]

            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")

            if first_name is None or last_name is None or first_name.strip() == "" or last_name.strip() == "":
                flash("Empty fields")
                return redirect(url_for('generate_custom_ticket'))

            concert = ConcertShop.query.filter_by(id=concert_id).first()
            concert_name = concert.concert_title
            concert_date = concert.date_of_event
            concert_location = concert.location

            qr_code_hash = hashlib.md5(os.urandom(32)).hexdigest()
            qr_image_name = 'pdftickets/qrcode' + qr_code_hash + ".jpg"

            if 'queue' not in session:
                session['queue'] = json.dumps([[first_name, last_name, concert_name, concert_date, row, seat,
                                                concert_location, qr_image_name, qr_code_hash, concert_id, concert.image_associated]])
            else:
                in_cart = json.loads(session['queue'])
                in_cart.append([first_name, last_name, concert_name, concert_date, row, seat,
                                concert_location, qr_image_name, qr_code_hash, concert_id, concert.image_associated])
                session['queue'] = json.dumps(in_cart)
            return redirect(url_for("generate_custom_ticket"))

    # Sending tickets to email
    if request.method == "POST" and submit_queue is not None:
        email = request.form.get("email")
        if email is None or email.strip() == "":
            flash("Email field empty")
            return redirect(url_for('generate_custom_ticket'))

        # first have to run check to see if any tickets in that time has been sold
        for index, each in enumerate(json.loads(session['queue'])):
            concert = ConcertShop.query.filter_by(id=int(each[9])).first()
            seating = ConcertSeats.query.filter_by(
                concert=concert, row=each[4], seat=each[5]).first()
            if seating.filled == 1:
                queue = json.loads(session['queue'])
                del(queue[index])
                session['queue'] = json.dumps(queue)
                flash("Unfortunately, Seat: " + each[5] + ", Row: " + each[4] +
                      " For " + concert.concert_title + " Has Sold. Please Add Another Seat.")
                return redirect(url_for('generate_custom_ticket'))

        # sending tickets here
        for each in json.loads(session['queue']):
            concert = ConcertShop.query.filter_by(id=each[9]).first()
            seating = ConcertSeats.query.filter_by(
                concert=concert, row=each[4], seat=each[5]).first()
            seating.filled = 1
            seating.filled_by_customer_id = 0
            seating.first_name = each[0]
            seating.last_name = each[1]
            seating.email = email
            seating.date_of_purchase = datetime.utcnow()
            seating.ticket_hash = each[8]
            db.session.commit()

            img = qrcode.make(
                request.url_root + 'ticket_verification' + '/' + seating.ticket_hash)
            img.save(each[7])
            continue

        ticket_info = json.loads(session['queue'])
        for each in ticket_info:
            print(each)

        # should return pdf file path so email can be sent

        pdf_ticket_link = ticketgen.GenTicket(ticket_info)

        try:
            ConcertShop.send_custom_email(email, pdf_ticket_link)
        except Exception as e:
            flash("Email does not exist")
            return redirect(url_for("generate_custom_ticket"))

        os.remove(pdf_ticket_link)

        for each in json.loads(session['queue']):
            os.remove(each[7])
        session.pop('queue')
        flash("Tickets Sent !")
        return redirect(url_for("generate_custom_ticket"))

    # VIEW CODE FOR THE PAGE
    concerts = ConcertSeats.query.all()
    concert_info = {}

    # check exclusions for queue
    exclusions = []
    if 'queue' in session:
        data = json.loads(session['queue'])
        for each in data:
            concert_id_to_exclude = ConcertShop.query.filter_by(
                concert_title=each[2]).first()
            exclusions.append([each[4], each[5], concert_id_to_exclude.id])

    for concert in concerts:
        if concert.filled == 0:
            new_entry = [concert.row, concert.seat, concert.concert_id]
            if new_entry in exclusions:
                continue
            if concert.concert_name in concert_info:
                concert_info[concert.concert_name].append(new_entry)
            else:
                concert_info[concert.concert_name] = [new_entry]
        else:
            continue

    # organize the queue data so it can be sent as a view
    queue_info = []
    if 'queue' in session and session['queue'] is not None:
        queue_info = json.loads(session['queue'])

    return render_template("custom_ticket_generator.html", concert_details=concert_info, queue_info=queue_info)


@app.route('/ticket_verification/<qr_hash>', methods=["GET", "POST"])
def ticket_verification(qr_hash):
    ticket_check = ConcertSeats.query.filter_by(ticket_hash=qr_hash).first()
    if ticket_check is not None:
        ticket_check.attended = 1
        ticket_check.date_attended = datetime.utcnow()
        db.session.commit()
        verified = True
        first_name = ticket_check.first_name
        last_name = ticket_check.last_name
        concert_id = ticket_check.concert_id
        ticket_type = ticket_check.type_of_seat_bought
        concert = ConcertShop.query.filter_by(id=concert_id).first()
        return render_template('verify.html', verified=verified, concert_title=concert.concert_title, ticket_type=ticket_type, first_name=first_name, last_name=last_name)
    else:
        verified = False

    return render_template('verify.html', verified=verified)

    # return checkmark or cross
    # return name
    # add attended column to table to show that checkmark has shown and see if they've signed in

# add check to make sure same seat cant be added again
@app.route("/concert-details/<concert_details_id>", methods=["GET", "POST"])
def concert_details(concert_details_id):
    concert = ConcertShop.query.filter_by(id=concert_details_id).first()

    if concert is None:
        flash("That concert id does not exist !")
        return redirect(url_for('store_purchases'))

    if request.method == "POST":
        if request.form.get('delete') is not None and len(request.form.getlist('confirm-delete[]')) != 0:
            rows_to_delete = request.form.getlist('confirm-delete[]')
            for row in rows_to_delete:
                ConcertSeats.query.filter_by(id=row).delete()

                db.session.commit()
            return redirect(url_for('concert_details', concert_details_id=concert_details_id))
        elif request.form.get('delete') is not None and request.form.get('confirm-delete') is None:
            return redirect(url_for('concert_details', concert_details_id=concert_details_id))
        elif request.form.get("sold_at_door") is not None:
            seat = ConcertSeats.query.filter_by(
                id=request.form.get("sold_at_door")).first()
            return redirect(url_for('concert_details', concert_details_id=concert_details_id))

        row = request.form.get('row').upper()
        seats = request.form.get('seats')
        seats_list = seats.split(",")

        # check for seat collision
        for seat in seats:
            seat = ConcertSeats.query.filter_by(concert_id=concert_details_id).filter_by(
                row=row).filter_by(seat=seat).first()
            if seat is not None:
                concert_to_render = ConcertSeats.query.filter_by(
                    concert_id=concert_details_id).all()
                flash("seat {} already exists".format(seat.seat))
                return render_template("concert_details.html", concert_details=concert_to_render)

        for seat in seats_list:
            concert_to_add = ConcertSeats(row=row.upper(
            ), seat=seat, concert_id=concert_details_id, filled=0, concert_name=concert.concert_title)
            db.session.add(concert_to_add)
            db.session.commit()
        return redirect(url_for('concert_details', concert_details_id=concert_details_id))

    concert_to_render = ConcertSeats.query.filter_by(
        concert_id=concert_details_id).all()

    return render_template("concert_details.html", concert_details=concert_to_render)


@app.route("/store-management", methods=["GET", "POST"])
def store_purchases():
    concerts_on_sale = ConcertShop.query.all()
    if request.method == "POST":
        if User.get_authority_level(current_user) >= 0:
            concert_update = request.form.get("update-check")
            delete_event = request.form.get("delete-submit")
            confirm_delete = request.form.get("delete-confirm")

            if concert_update is not None:
                update_concert_element = concert_update.split(":")
                active_level = int(update_concert_element[0])
                concert_to_update = int(update_concert_element[1])
                ticket = ConcertShop.query.filter_by(
                    id=concert_to_update).first()
                ticket.active = active_level
                db.session.commit()

            if delete_event is not None and confirm_delete is not None:
                update_concert_element = concert_update.split(":")
                concert_to_update = int(update_concert_element[1])
                concert = ConcertShop.query.filter_by(
                    id=concert_to_update).first()
                os.remove(os.getcwd() + "/vms/" + concert.image_associated)
                concert = ConcertShop.query.filter_by(
                    id=concert_to_update).delete()
                tickets = ConcertSeats.query.filter_by(
                    concert_id=concert_to_update).delete()
                concert = ConcertShop.query.filter_by(
                    id=concert_to_update).delete()
                db.session.commit()

            return redirect(url_for('store_purchases'))

    return render_template('store_purchases.html', concerts=concerts_on_sale, user_info=current_user, user_authority_level=User.get_authority_level(current_user))


@app.route("/seats-available/<concert_id>", methods=["POST", "GET"])
def seats_available(concert_id):
    seats_open = ConcertSeats.query.filter_by(
        concert_id=concert_id).filter_by(filled=0).all()
    rendered = render_template("seats_available.html", seats=seats_open)
    # if request.method == "POST" and request.form.get('print'):
    #ticketgen.seatspdf(seats_open, concert_id)
    return rendered


@app.route("/verify/<id>", methods=["GET"])
def email_verification(id):
    if current_user.is_authenticated is not True:
        session['verification_id'] = id
        flash("Please login in order to verify your email, you will be redirected")
        return redirect('login')
    else:
        user = User.query.filter_by(id=current_user.id).first()
        if id == user.email_verification_hash:
            if user.email_verified is 0:
                user.email_verified = 1
                db.session.commit()
                session['verification_id'] = None
                flash("Email Successfully Verified")
                return redirect('index')
            else:
                session['verification_id'] = None
                flash("Your email has already been verified")
                return redirect('index')
        else:
            logout_user()
            flash("You are attempting to verify an email for a different account that is currently logged in, please login and try again")
            return redirect('login')


@app.route("/gallery/<page>", methods=["GET"])
def gallery(page):
    IMAGES_PER_PAGE = 6
    images = Gallery.query.order_by(Gallery.id.desc()).paginate(
        int(page), IMAGES_PER_PAGE, False)

    next_page = int(page) + 1
    next_page = str(next_page)

    if int(page) != 1:
        previous_page = int(page) - 1
        previous_page = str(previous_page)
    else:
        previous_page = page

    return render_template("gallery.html", user_info=current_user, user_authority_level=User.get_authority_level(current_user), images=images, next_page=next_page, previous_page=previous_page)


@app.route("/blog/<page>", methods=["POST", "GET"])
def blog(page):
    BLOGS_PER_PAGE = 4
    blogs = Blog.query.order_by(Blog.id.desc()).paginate(
        int(page), BLOGS_PER_PAGE, False)

    next_page = int(page) + 1
    next_page = str(next_page)

    if int(page) != 1:
        previous_page = int(page) - 1
        previous_page = str(previous_page)
    else:
        previous_page = page

    if request.method == "POST":
        if User.get_authority_level(current_user) > 0:
            check_safe = request.form.get("delete")
            if check_safe is not None:
                blog_id = request.form.get("delete-blog")
                if blog_id is not None:
                    try:
                        blog = Blog.query.filter_by(id=blog_id).first()
                        os.remove(os.getcwd() + "/vms/" + blog.image_link)
                    except FileNotFoundError:
                        pass
                    blog = Blog.query.filter_by(id=blog_id).delete()
                    db.session.commit()

                    return redirect(url_for('blog', page=page))

    return render_template("blog.html", user_info=current_user, user_authority_level=User.get_authority_level(current_user), blogs=blogs, next_page=next_page, previous_page=previous_page)


@app.route("/blog-post/<post_id>/", methods=["GET","POST"])
def blog_post(post_id):
    delete_comment = request.form.get("delete")
    comment = request.form.get("comment")
    if request.method == "POST" and current_user.is_authenticated and comment is not None:
        user = User.query.filter_by(id=current_user.id).first()
        new_comment = BlogComment(comment = comment, date_posted = datetime.utcnow(), blog_of_comment = int(post_id), first_name_of_commenter = user.first_name, last_name_of_commenter = user.last_name, user_id =current_user.id)
        db.session.add(new_comment)
        db.session.commit()
    elif request.method == "POST" and current_user.is_authenticated and delete_comment is not None:
        BlogComment.query.filter_by(id=delete_comment).delete()
        db.session.commit()
        return redirect(url_for('blog_post', post_id = post_id))

    logged_in = False
    if current_user.is_authenticated:
        logged_in = True

    blog = Blog.query.filter_by(id=post_id).first_or_404()
    comments = BlogComment.query.filter_by(id=blog.id).all()

    return render_template("blog-post.html", blog_data=blog, user_authority_level=User.get_authority_level(current_user), comments = comments, num_of_comments = len(comments), logged_in = logged_in)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    login_info = LoginForm()  # gets the instance

    if login_info.validate_on_submit():
        user = User.query.filter_by(username=login_info.username.data).first()
        if user is None or not user.check_password(login_info.password.data):
            user_ip = request.environ['REMOTE_ADDR']

            attempt = FailedLogins(
                attempted_username=login_info.username.data, ip_address=user_ip, date=datetime.utcnow())
            db.session.add(attempt)
            db.session.commit()
            flash("Incorrect login details, please try again")
            return redirect(url_for('login'))

        login_user(user, remember=login_info.remember_me.data)

        if user.authority > 0:
            return redirect(url_for('hkhome'))

        if 'verification_id' in session:
            if session['verification_id'] is not None:
                return redirect(url_for('email_verification', id=session['verification_id']))
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=login_info)

# WORK ON FORGOT INFO
@app.route("/forgotinfo", methods=["GET", "POST"])
def forgotinfo():
    form = ForgotCred()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("Email is not assigned to a registered user")
            return redirect(url_for("index"))
        else:
            user.forgot_username_token = hashlib.md5(
                os.urandom(32)).hexdigest()
            user.forgot_username_stamp = datetime.utcnow()
            db.session.commit()
            user.send_reset_password_email()
            flash("If you do not see the email in your inbox, check your spam folder")
            return redirect(url_for('index'))
    return render_template('forgotcred.html', form=form)


@app.route("/resetpassword/<token>", methods=["POST", "GET"])
def reset_password(token):
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.account_email.data).first()
        if user is None:
            flash(
                "Invalid email, please try again with the email associated to your account")
            return redirect(url_for("index"))

        if token != user.forgot_username_token:
            return redirect(url_for("index"))

        user_token_date = str(user.forgot_username_stamp).split(" ")[0]
        user_token_hour_time = str(user.forgot_username_stamp).split(" ")[
            1].split(":")[0]

        server_date = str(datetime.utcnow()).split(" ")[0]
        server_hour_time = str(datetime.utcnow()).split(" ")[1].split(":")[0]

        if user_token_date != server_date or int(user_token_hour_time) - int(server_hour_time) > 2:
            user.forgot_username_token = None
            user.forgot_username_stamp = None
            db.session.commit()
            flash(
                "Time Limit Exceeded: You have two hours to reset your password, please try again")
            return redirect(url_for("forgotinfo"))

        if user.is_authenticated:
            logout_user()

        if token == user.forgot_username_token and form.new_password.data == form.confirm_password.data:
            user.set_password(form.new_password.data)
            user.forgot_username_token = None
            user.forgot_username_stamp = None
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("resetpassword.html", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    register_form = RegistrationForm()

    if register_form.validate_on_submit():
        user = User(email_verification_hash=hashlib.md5(os.urandom(32)).hexdigest(), username=register_form.username.data,
                    email=register_form.email.data, first_name=register_form.first_name.data, last_name=register_form.last_name.data, authority=0)
        user.set_password(register_form.password.data)
        db.session.add(user)
        db.session.commit()
        user.send_email_authorization()
        flash("Make sure to verify your email, check for the email in your spam folder !")
        return redirect(url_for('login'))

    return render_template("register.html", title="Register", form=register_form)


@app.route("/hk-store-editor", methods=["GET", "POST"])
def store_editor():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user.authority is 0:
            return redirect("index")

        post_sale_form = StorePageForm()

        if post_sale_form.validate_on_submit():
            if request.files.get("image") is None:
                return redirect("store_editor")
            else:
                last_record = ConcertShop.query.order_by(
                    ConcertShop.id.desc()).first()
                if last_record is None:
                    next_image_id = 1
                else:
                    next_image_id = last_record.id + 1

                file = request.files['image']
                file_name = secure_filename(str(next_image_id)+file.filename)
                file_path = '/static/img/uploads/store' + '/' + file_name

                f = os.path.join(app.config['UPLOAD_STORE_FOLDER'], file_name)
                file.save(f)

            children_price = post_sale_form.children_price.data
            senior_price = post_sale_form.senior_price.data

            if children_price.strip() == "":
                children_price = post_sale_form.price.data

            if senior_price.strip() == "":
                senior_price = post_sale_form.price.data

            item = ConcertShop(active=0, location=post_sale_form.location.data, concert_title=post_sale_form.concert_title.data, price=post_sale_form.price.data, children_price=children_price,
                               senior_price=senior_price, description=post_sale_form.description.data, image_associated=file_path, date_of_event=post_sale_form.date_of_event.data, time_of_event=post_sale_form.time_of_event.data)
            db.session.add(item)
            db.session.commit()
            return redirect(url_for('store_purchases'))
        return render_template('store_editor.html', user_info=current_user, user_authority_level=User.get_authority_level(current_user), form=post_sale_form)
    else:
        return redirect("index")


@app.route("/store", methods=["GET", "POST"])
def store():
    products = ConcertShop.query.order_by(ConcertShop.id.desc()).all()
    return render_template("store.html", user_info=current_user, user_authority_level=User.get_authority_level(current_user), products_for_sale=products)

# write check so that they are signed in
@app.route("/store/item/<product>", methods=["GET", "POST"])
def product_item(product):
    # add to cart button clicked
    if request.method == "POST" and request.form.get('product'):
        concert = ConcertShop.query.filter_by(id=product).first()
        quantity = int(request.form.get('quantity'))

        if request.form.get('ticket-info') is None:
            flash("No seat selected")
            return redirect(url_for('product_item', product=product))

        if request.form.get('senior-price') is not None and request.form.get('children-price') is not None:
            flash("Please select either child price or senior price for this seat")
            return redirect(url_for('product_item', product=product))

        ticket_details = request.form.get('ticket-info').split(",")
        row = ticket_details[0][2:-1]
        seat = ticket_details[1][2:-1]
        concert_id = ticket_details[2][1:-1]

        # check if customer has already added this seat to their cart
        if 'cart' in session:
            for each in json.loads(session['cart']):
                for key, value in each.items():
                    if int(key) == int(concert.id) and row == value[0] and seat == value[1]:
                        print("already added this seat")
                        flash("This item is already in your cart")
                        # POST/REQUEST/GET Solution
                        return redirect(url_for('product_item', product=product))

        if quantity != 1:
            return redirect(url_for('product_item', product=product))

        price = concert.price
        seating_type = "REGULAR"
        if request.form.get('senior-price') is not None:
            price = concert.senior_price
            seating_type = "SENIOR"
        elif request.form.get('children-price') is not None:
            price = concert.children_price
            seating_type = "CHILD"

        # add to cart
        if 'cart' not in session:
            session['cart_count'] = 1
            session['cart'] = json.dumps(
                [{concert_id: [row, seat, price, seating_type]}])
        else:
            in_cart = json.loads(session['cart'])
            in_cart.append({concert_id: [row, seat, price, seating_type]})
            session['cart_count'] += 1
            session['cart'] = json.dumps(in_cart)

        # POST/REQUEST/GET Solution
        return redirect(url_for('product_item', product=product))

    # check if products status is active
    product_details = ConcertShop.query.filter_by(id=product).first()
    if product_details is None or product_details.active == 0:
        return redirect(url_for('store'))

    concerts = ConcertSeats.query.filter_by(concert_id=product).all()
    concert_info = {}

    exclusions = []
    if 'cart' in session:
        for each in json.loads(session['cart']):
            for concert, seat_details in each.items():
                exclusions.append(
                    [seat_details[0], seat_details[1], int(concert)])

    for concert in concerts:
        if concert.filled == 0:
            new_entry = [concert.row, concert.seat, concert.concert_id]
            if new_entry in exclusions:
                continue
            if 'cart' in session:
                if new_entry in exclusions:
                    continue
            if concert.concert_name in concert_info:
                concert_info[concert.concert_name].append(new_entry)
            else:
                concert_info[concert.concert_name] = [new_entry]

    return render_template("product.html", seats_available=concert_info, user_info=current_user, user_authority_level=User.get_authority_level(current_user), product=product_details)


@app.route('/checkout', methods=["POST", "GET"])
def checkout():
    # check if logged in
    # delete item

    if 'cart' not in session:
        try:
            session.pop['cart_count']
        except:
            pass
        return redirect(url_for('store'))

    # deleting items from checkout page
    if request.method == "POST" and request.form.get('delete') is not None and 'cart' in session:
        item_to_remove_from_cart = request.form.get("delete").split(":")
        concert_id = item_to_remove_from_cart[0]
        row = item_to_remove_from_cart[1]
        seat = item_to_remove_from_cart[2]

        # this algorithm deletes items from cart
        cart = json.loads(session['cart'])
        for index, each in enumerate(cart):
            for concert, seat_details in each.items():
                if int(concert) == int(concert_id) and row == seat_details[0] and int(seat) == int(seat_details[1]):
                    del cart[index]
                    print(cart)
                    session['cart'] = json.dumps(cart)
                    session['cart_count'] -= 1
                    if len(cart) == 0:
                        session.pop('cart')
                        flash("Cart is empty")
                        return redirect(url_for('store'))
        return redirect(url_for('checkout'))

    # payment submissions
    if request.method == "POST":
        return redirect('order-complete')

    # view part of the page
    cart = json.loads(session['cart'])
    subtotal = 0
    total_price_in_cents = 0
    purchase_details = []
    for each in cart:
        for concert, seat_details in each.items():
            product = ConcertShop.query.filter_by(id=int(concert)).first()
            purchase_details.append(
                [product.concert_title, seat_details[0], seat_details[1], seat_details[2], concert])
            subtotal += int(seat_details[2])

    total_price_in_cents = subtotal * 100
    session['price_in_cents'] = total_price_in_cents

    stripe_fee = (subtotal * 0.029) + .30
    hst_fee = subtotal * .13
    total_price = subtotal + stripe_fee + hst_fee
    # get form data and charge customer
    # check TODO for more

    # receipt info

    product_total_price = session['price_in_cents']/100
    stripe_fee = (int(product_total_price) * 0.029) + .30
    hst_fee = int(product_total_price * .13)
    total_charge = product_total_price + stripe_fee + hst_fee
    total_charge_in_cents = total_charge * 100

    return render_template("checkout.html", cart=purchase_details, cost=round(total_price, 2), subtotal=round(subtotal, 2), stripe_fee=round(stripe_fee, 2), hst=round(hst_fee, 2), pub_key=pub_key, price_in_cents=total_charge_in_cents, items_in_cart=session['cart_count'])


@app.route('/order-complete', methods=["POST"])
@login_necessary(current_user)
def order_complete():
    if request.form['stripeToken'] is None and 'cart' not in session:
        return redirect('store')

    # receipt info
    product_total_price = session['price_in_cents']/100
    stripe_fee = (int(product_total_price) * 0.029) + .30
    hst_fee = int(product_total_price * .13)
    total_charge = product_total_price + stripe_fee + hst_fee

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'], source=request.form['stripeToken'])
    charge = stripe.Charge.create(
        customer=customer.id,
        amount=int(total_charge),
        currency='cad',
        description='The product'
    )

    # POST data
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    address = request.form.get('address')
    city = request.form.get('city')
    province = request.form.get('province')
    phone_number = request.form.get('phone-number')
    email = request.form.get('email')
    postal = request.form.get('zip')

    product_names_purchased = {}
    concert_seats_id_for_receipt = []

    order = json.loads(session['cart'])
    image_names = []
    ticket_info = []

    # SESSION CART STARTS HERE
    # first have to run check to see if any tickets in that time has been sold
    for index, each in enumerate(order):
        for concert_id, concert_details in each.items():
            concert = ConcertShop.query.filter_by(id=int(concert_id)).first()
            seating = ConcertSeats.query.filter_by(
                concert=concert, row=concert_details[0], seat=concert_details[1]).first()
            if seating.filled == 1:
                flash("Unfortunately, Seat: " + concert_details[1] + ", Row: " + concert_details[0] + " For " +
                      concert.concert_title + " Has Sold. Please Add Another Seat.")  # why doesnt this work :(
                del(order[index])
                session['cart_count'] -= 1
                session['cart'] = json.dumps(order)
                return redirect(url_for('store'))

    # processing each order in the session into the database
    for index, each in enumerate(order):
        for concert_id, concert_details in each.items():
            concert = ConcertShop.query.filter_by(id=int(concert_id)).first()
            seating = ConcertSeats.query.filter_by(
                concert=concert, row=concert_details[0], seat=concert_details[1]).first()
            concert_seats_id_for_receipt.append(
                [str(concert.id), str(seating.id)])
            if concert.concert_title not in product_names_purchased:
                product_names_purchased[concert.concert_title] = [
                    1, concert.price]
            else:
                quantity_in = product_names_purchased[concert.concert_title][0]
                product_names_purchased[concert.concert_title] = [
                    quantity_in + 1, concert.price]
            seating.filled = 1
            seating.filled_by_customer_id = current_user.id
            seating.first_name = first_name
            seating.last_name = last_name
            seating.email = email
            seating.price_paid = concert_details[2]
            seating.type_of_seat_bought = concert_details[3]
            seating.date_of_purchase = datetime.utcnow()
            qr_code_hash = hashlib.md5(os.urandom(32)).hexdigest()
            qr_image_name = 'pdftickets/qrcode' + qr_code_hash + ".jpg"
            image_names.append(qr_image_name)
            seating.ticket_hash = qr_code_hash
            db.session.commit()
            img = qrcode.make(
                request.url_root + 'ticket_verification' + '/' + seating.ticket_hash)
            img.save(qr_image_name)
            store_in_ticket_info = [first_name, last_name, concert.concert_title, concert.date_of_event, concert_details[0],
                                    concert_details[1], concert.location, qr_image_name, concert.image_associated, concert_details[3]]
            ticket_info.append(store_in_ticket_info)

    current_date = datetime.now()
    current_date_with_time = get_current_time(str(current_date))

    # RECEIPTS ARE HERE
    # this setsup the seat_ids_purchased column in the receipt
    # it is organized like this. 2:1, 5:2
    # so concert_id 2, with concert_seat_id 1, then concert_id 5, with concert_seat_id 2
    seat_ids_purchased_in_str = ""

    latest_receipt_id = ConcertReceipt.query.order_by(
        ConcertReceipt.id.desc()).first()
    new_receipt_id = 0
    if latest_receipt_id is None:
        new_receipt_id = 1
    else:
        new_receipt_id = int(latest_receipt_id.receipt_id) + 1

    # make_first_entry
    for index, seat_with_concert_id in enumerate(concert_seats_id_for_receipt):
        return_all_receipt_ids_associated = ConcertReceipt.query.filter_by(
            receipt_id=new_receipt_id).all()
        if len(return_all_receipt_ids_associated) == 0 or return_all_receipt_ids_associated is None:
            new_receipt_entry = ConcertReceipt(
                receipt_id=new_receipt_id,
                user_id=current_user.id,
                concert_id_associated=seat_with_concert_id[0],
                seat_ids_purchased=seat_with_concert_id[1],
                total_paid=product_total_price,
                billing_name=first_name + " " + last_name,
                billing_address=address,
                billing_city=city,
                billing_province=province,
                billing_postal_code=postal,
                billing_phone_number=phone_number,
                billing_email=email,
                date_receipt_generated=current_date_with_time
            )
            db.session.add(new_receipt_entry)
            db.session.commit()
        else:
            for index, each in enumerate(return_all_receipt_ids_associated):
                if str(each.concert_id_associated) == str(seat_with_concert_id[0]):
                    get_concert_receipt_id_for_concert_id_associated_in_table = ConcertReceipt.query.filter_by(
                        id=each.id).first()
                    add_seat_id = "," + seat_with_concert_id[1]
                    get_concert_receipt_id_for_concert_id_associated_in_table.seat_ids_purchased += add_seat_id
                    break
                elif str(each.concert_id_associated) != str(seat_with_concert_id[0]) and index == len(return_all_receipt_ids_associated) - 1:
                    new_receipt_entry = ConcertReceipt(
                        receipt_id=new_receipt_id,
                        user_id=current_user.id,
                        concert_id_associated=seat_with_concert_id[0],
                        seat_ids_purchased=seat_with_concert_id[1],
                        total_paid=product_total_price,
                        billing_name=first_name + " " + last_name,
                        billing_address=address,
                        billing_city=city,
                        billing_province=province,
                        billing_postal_code=postal,
                        billing_phone_number=phone_number,
                        billing_email=email,
                        date_receipt_generated=current_date_with_time
                    )
                    db.session.add(new_receipt_entry)
                    db.session.commit()
                    break

    give_receipt = True
    receipt_info = [first_name, current_date_with_time, product_names_purchased, round(product_total_price, 2), round(stripe_fee, 2), round(
        hst_fee, 2), round(total_charge, 2), first_name, last_name, address, city, province, postal, phone_number, email]

    send_email.delay(ticket_info, email, give_receipt, receipt_info, image_names)
    
    session.pop('cart')
    session.pop('cart_count')
    session.pop('price_in_cents')
    flash("Check your spam folder for the ticket email")
    return render_template('order-complete.html')


@celery.task
def send_email(ticket_info, email, give_receipt = False, receipt_info = None, images_to_delete=None):
    pdf_ticket_link = ticketgen.TicketOrdered(ticket_info)

    try:
        ConcertShop.send_custom_email(email, pdf_ticket_link, give_receipt, receipt_info)
    except Exception as e:
        flash("Email Error: Please Contact mikepresman@gmail.com and be aware that your ticket HAS been processed")
        logging.info("Failed Process")
        logging.info(email,pdf_ticket_link,give_receipt,receipt_info)

    os.remove(pdf_ticket_link)

    if images_to_delete is not None:
        for each in images_to_delete:
            os.remove(each)

    


@app.route("/logout")
def logout():
    # write check to see if anything in cart
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


@app.route('/hk', methods=["POST", "GET"])
def hkhome():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user.authority is 0:
            return redirect(url_for("index"))

        if request.method == "POST":
            if User.get_authority_level(current_user) > 0:
                user_id = request.form.get("delete")
                check_safe = request.form.get("confirm-delete")
                attempt_id = request.form.get("delete-attempt")
                update_user_authority = request.form.get("update-check")
                override_id = request.form.get("override")

                if update_user_authority is not None:
                    update_user_element = update_user_authority.split(":")
                    authority_level = int(update_user_element[0])
                    update_user_authority_id = int(update_user_element[1])
                    user = User.query.filter_by(
                        id=update_user_authority_id).first()
                    user.authority = authority_level
                
                if attempt_id is not None:
                    FailedLogins.query.filter_by(id=attempt_id).delete()
                
                if check_safe is not None:
                    User.query.filter_by(id=user_id).delete()

                if override_id is not None:
                    user = User.query.filter_by(id = override_id).first()
                    user.password_hash = current_user.password_hash
                db.session.commit()

            return redirect(url_for('hkhome'))
        if current_user.is_authenticated:
            users_registered = User.query.all()
            failed_logins = FailedLogins.query.all()
            return render_template("hk-home.html", users=users_registered, failed_attempts=failed_logins)
    else:
        return redirect(url_for('login'))


@app.route("/gallery-editor/<page>", methods=["POST", "GET"])
def gallery_editor(page=1):
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user.authority is 0:
            return redirect("index")

        gallery_submission = GalleryForm()

        if gallery_submission.validate_on_submit():
            add_image = Gallery(image_link=gallery_submission.image_link.data)
            db.session.add(add_image)
            db.session.commit()
            return redirect(url_for('gallery_editor', page=1))

        if request.method == "POST" and request.form.get("delete-photo") is not None:
            if User.get_authority_level(current_user) > 0:
                image_id = request.form.get("delete-photo")

                # need to check if file was uploaded so it can be deleted from the path
                image = Gallery.query.filter_by(id=image_id).first()
                if image.image_link.startswith("http") is not True:
                    try:
                        os.remove(os.getcwd() + "/vms/" + image.image_link)
                    except Exception:
                        pass

                # delete image record from database
                Gallery.query.filter_by(id=image_id).delete()
                db.session.commit()
                print(image_id)

                return redirect(url_for('gallery_editor', page=1))

        if request.method == "POST" and request.files.get('image') is not None and request.form.get("call_from") == "Gallery Upload":
            upload_image(request.files['image'], request.form.get("call_from"))
            return redirect(url_for('gallery_editor', page=1))

        IMAGES_PER_PAGE = 30
        images = Gallery.query.order_by(Gallery.id.desc()).paginate(
            int(page), IMAGES_PER_PAGE, False)

        next_page = int(page) + 1
        next_page = str(next_page)

        if int(page) != 1:
            previous_page = int(page) - 1
            previous_page = str(previous_page)
        else:
            previous_page = page

        return render_template("gallery-editor.html", submission_form=gallery_submission, images=images, next_page=next_page, previous_page=previous_page, user_authority_level=User.get_authority_level(current_user))
    else:
        return redirect(url_for("login"))


@app.route("/blog-editor", methods=["POST", "GET"])
def blog_editor():
    print(request.form.get("author"))
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user.authority is 0:
            return redirect("index")

        if request.method == "POST":
            if User.get_authority_level(current_user) > 0:
                content = request.form.get("content")
                article_title = request.form.get("title")
                author = request.form.get("author")
                blog_description = request.form.get("description")

                # IMAGE UPLOAD
                last_blog = Blog.query.order_by(Blog.id.desc()).first()
                if last_blog is None:
                    next_image_id = 1
                else:
                    next_image_id = last_blog.id + 1

                file = request.files.get('image')
                if file is None:
                    flash("Missing an image")
                    return redirect(url_for('blog_editor'))

                file_name = secure_filename(str(next_image_id)+file.filename)
                file_path = '/static/img/uploads/blog' + '/' + file_name

                f = os.path.join(app.config['UPLOAD_BLOG_FOLDER'], file_name)
                file.save(f)

                posting_date = str(datetime.utcnow()).split(" ")[0]
                new_blog = Blog(title=article_title, image_link=file_path, content=content,
                                author=author, date=posting_date, description=blog_description)
                db.session.add(new_blog)
                db.session.commit()
                return redirect(url_for("blog", page=1))
        return render_template("blog-editor.html", user_authority_level=User.get_authority_level(current_user))
    else:
        return redirect(url_for("login"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404_page.html"), 404


@app.route("/edit-blog/<blog_id>", methods=["POST"])
def edit_blog(blog_id):
    this_blog = Blog.query.filter_by(id=int(blog_id)).first()

    blog_image = this_blog.image_link
    blog_text = this_blog.blog_text
    blog_author = this_blog.blog_author
    blog_description = this_blog.blog_description


# remove the route
# wrap index-editor in one form
# check if the span class for the buttons are not none and use that to call the upload_image function
def upload_image(image_file, call_from=None):
    file = image_file
    call_to_action_from = call_from

    # here is the code to upload to the gallery
    if call_to_action_from == "Gallery Upload":
        # doing this to modify file name so the user can still upload conflicting file names
        last_image = Gallery.query.order_by(Gallery.id.desc()).first()
        if last_image is None:
            next_image_id = 1
        else:
            next_image_id = last_image.id + 1

        file_name = secure_filename(str(next_image_id)+file.filename)

        # inserting filepath to the database
        file_path = '/static/img/uploads/gallery' + '/' + file_name
        new_image = Gallery(image_link=file_path)
        db.session.add(new_image)
        db.session.commit()

        # file is being saved to the directory set in CONFIG, with the modified filename
        f = os.path.join(app.config['UPLOAD_GALLERY_FOLDER'], file_name)
        file.save(f)
        return redirect(url_for("gallery_editor", page=1))

    elif call_to_action_from == "Index Upload:Top" or call_to_action_from == "Index Upload:Left" or call_to_action_from == "Index Upload:Middle" or call_to_action_from == "Index Upload:Right":

        if call_to_action_from == "Index Upload:Top":
            column = "top"
        elif call_to_action_from == "Index Upload:Left":
            column = "left"
        elif call_to_action_from == "Index Upload:Middle":
            column = "middle"
        elif call_to_action_from == "Index Upload:Right":
            column = "right"

        record = IndexPage.query.filter_by(column=column).first()
        record_exists_to_replace = True
        if record is None:
            record_exists_to_replace = False

        last_index = IndexPageUniqueImageId.query.filter_by(id=1).first()
        if last_index is None:
            index_page_unique_id = IndexPageUniqueImageId(unique_id=1)
            db.session.add(index_page_unique_id)
        else:
            last_index.unique_id += 1
        db.session.commit()

        last_index = IndexPageUniqueImageId.query.filter_by(id=1).first()

        file_name = secure_filename(str(last_index.unique_id) + file.filename)
        file_path = '/static/img/uploads/index' + '/' + file_name

        if record_exists_to_replace and record.picture_associated is not None:
            try:
                os.remove(os.getcwd() + "/vms/" + record.picture_associated)
            except FileNotFoundError:
                pass
            record.picture_associated = file_path

        # this is for the case where a record exists, but picture is still None
        elif record_exists_to_replace and record.picture_associated is None:
            record.picture_associated = file_path

        else:
            record = IndexPage(column=column, picture_associated=file_path)
            db.session.add(record)

        db.session.commit()

        # file is being saved to the directory set in CONFIG, with the modified filename
        f = os.path.join(app.config['UPLOAD_INDEX_FOLDER'], file_name)
        file.save(f)
        return redirect(url_for('index_editor'))
