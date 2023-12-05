from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, Response, current_app
from flask_login import login_required, current_user
from .models import Note, FilamentInventory
from . import db
import json
from .nfc_util_NXP import get_nfc_uid_from_reader
import cv2
from pyzbar.pyzbar import decode
from picamera2 import Picamera2
from sqlalchemy.exc import IntegrityError


views = Blueprint('views', __name__)
picam2 = None
last_scanned_sku = None

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    filament_inventory = FilamentInventory.query.all()

    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user, filament_inventory=filament_inventory)


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

@views.route('/start_camera')
def start_camera():
    global picam2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
    return '', 204  # Return an empty response with a 204 status code

@views.route('/stop_camera')
def stop_camera():
    global picam2
    if picam2:
        picam2.stop()
        picam2 = None
    return '', 204

def draw_barcode_frame(frame, barcode, text):
    """Function to draw barcode rectangle and text on the frame."""
    frame = cv2.rectangle(frame, (barcode.rect.left, barcode.rect.top),
                          (barcode.rect.left + barcode.rect.width, barcode.rect.top + barcode.rect.height), (0, 255, 0), 3)
    frame = cv2.putText(frame, text, (barcode.rect.left, barcode.rect.top + barcode.rect.height),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
    return frame

@views.route('/video_feed')
def video_feed():
    def gen_frames():
        global last_scanned_sku
        global picam2
        while True:
            if picam2:
                frame = picam2.capture_array()
                if frame is not None:
                    # Rotate the frame 90 degrees clockwise
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

                    for d in decode(frame):
                        s = d.data.decode()
                        last_scanned_sku = s  # Update the last scanned SKU
                        frame = draw_barcode_frame(frame, d, s)
                    
                    encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame + b'\r\n\r\n'
                else:
                    print('Error capturing frame')
                    break
            else:
                print('Exit the loop, camera is not started')
                break

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/update_weight', methods=['POST'])
def update_weight():
    global last_scanned_sku
    data = request.get_json()
    weight = data.get('weight')

    if last_scanned_sku:
        sku = last_scanned_sku

        filament = FilamentInventory.query.filter_by(sku=sku).first()

        if not filament:
            # Create a new entry if SKU does not exist
            filament = FilamentInventory(sku=sku, weight=weight)
            db.session.add(filament)
        else:
            # Update the weight if SKU exists
            filament.weight = weight

        try:
            db.session.commit()
            last_scanned_sku = None
            return jsonify({"message": "Weight updated successfully"}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Failed to update weight"}), 500
    else:
        return jsonify({"error": "No SKU scanned"}), 400
