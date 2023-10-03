from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
#from .nfc_util import get_nfc_uid_from_reader
from .nfc_util_NXP import get_nfc_uid_from_reader

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/user', methods=['GET'])
@login_required
def user_page():
    # Any logic to fetch user-specific data can go here
    # For example, fetch the user's notes, profile details, etc.
    
    return render_template('user.html', user=current_user)

@views.route('/add-nfc-card', methods=['POST'])
@login_required
def add_nfc_card():
    nfc_uid = get_nfc_uid_from_reader()  # Fetch the NFC UID using the reader
    if nfc_uid:
        current_user.nfc_uid = nfc_uid
        db.session.commit()
        flash('NFC card added successfully!', category='success')
    else:
        flash('Failed to read NFC card. Please try again.', category='error')
    return redirect(url_for('views.user_page'))

@views.route('/inventory', methods=['GET'])
@login_required
def inventory():
    return render_template('inventory.html', user=current_user)

@views.route('/handle-qr-code', methods=['POST'])
@login_required
def handle_qr_code():
    data = request.json
    qr_code = data.get('qrCode')

    print(qr_code)

    # Handle the QR code as needed
    # For example, you might want to search an inventory database, 
    # log the scan, etc.

    return jsonify({"message": "QR code received", "qrCode": qr_code})
