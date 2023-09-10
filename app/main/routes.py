import os
import cv2
import numpy as np
from flask import flash, request, render_template, get_flashed_messages
from app.main import bp

UPLOAD_FOLDER = './app/static/'
BASEDIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_PATH = os.path.join(BASEDIR, UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@bp.route('/', methods=['GET'])
def index():
    get_flashed_messages()
    return render_template('index.html')


@bp.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'uploaded-file' not in request.files:
            flash('Error in the reauest file part not found')
            return render_template("index.html")
        file = request.files['uploaded-file']
        img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        # check if file has name and is uploaded
        if file.filename == '':
            flash('No file selected')
            return render_template("index.html")
        # check if file extensions is allowed
        if not allowed_file(file.filename):
            flash('File name not allowed or wrong file type')
            return render_template("index.html")
        # check if file is of the right dimensions
        if not allowed_dimensions(img):
            flash('File is not 512X512')
            return render_template("index.html")
        # check if image is only in the circle
        if not check_non_transparent(img):
            flash('File has non-transparent points outside of the circle')
            return render_template("index.html")
        # check if image is happy
        if not check_happiness(img):
            flash('Choosen Avatar has not a happy feeling')
            return render_template("index.html")
        if file:
            file.seek(0)
            print(os.path.join(UPLOAD_PATH,"avatar.png"))
            file.save(os.path.join(UPLOAD_FOLDER,"avatar.png"))
            return render_template('index.html')

@bp.context_processor
def handle_context():
    return dict(os=os)

def allowed_file(filename):     
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_dimensions(img):
    h, w, _ = img.shape
    return h == 512 and w == 512

def check_non_transparent(img):
    h, w, _ = img.shape

    # get image with transparency values
    imgTransp = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    # define circle dimensions (in our case we could hard code it but this could work with any square image)
    center = (h/2,w/2)
    radius = max(h,w)/2
    # Iterate through all the pixels in the image
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            if not is_inside(img[row][col], center, radius) and imgTransp[row][col][3] != 255:
                return False
    return True

def is_inside(point, center, radius):
    eqn = (point[0] - center[0]) ** 2 + (point[1] - center[1])**2 - radius**2
    return eqn <= 0

def check_happiness(img):
    avg_color_per_row = np.average(img, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    unique_rgb,counts = np.unique(avg_color,return_counts=True)
    if avg_color[0]+avg_color[1]+avg_color[2]<255 and check_color(unique_rgb,counts):
        return False
    else:
        return True

def check_color(colors, counts):
    for i in range(0,len(colors)):
        if colors[i] == 0 and counts[i]==2:
            return True
    return False