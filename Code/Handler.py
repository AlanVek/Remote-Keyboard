# Networking
from http.server import BaseHTTPRequestHandler

# Keyboard
from keyDict import *
from mouseDict import *
# from pyautogui import move

# URL parsing
from urllib.parse import unquote

# PyInstaller patches
import sys
from os.path import abspath, join

# Keywords
KEYWORD_KEY = '__special__'
KEY_SEPARATOR = '__separator__'
QUESTION = '__sign__'
KEYWORD_EXIT = '__exit__'
HOTKEY = 'hotkey'
DIST = 5
MOUSE = '__mouse__'
CLICK = '__click__'

# Workaround for PyInstaller dependencies.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = abspath(".")

    return join(base_path, relative_path)

# Updates Behaviour.js with current IP for requests.
def update_ip(cls):
    with open(resource_path('.\\templates\\js\\Keyboard.js'), 'rt') as file: data = file.read()

    data = data.replace(data[data.find('const ip =') : data.find('const ip =') + 39], f"const ip = 'http://{cls.IP}:8000/'; ")
    with open(resource_path('.\\templates\\js\\Keyboard.js'), 'wt') as file: file.write(data)

# Class RHandler for server.
class RHandler(BaseHTTPRequestHandler):

    running = True
    selection = False
    # w, h = size()

    # Project files
    files = {
        'html' : '',
        'js_beh' : '',
        'js_key' : '',
        'js_mouse': '',
        'css' : ''
    }

    # Sends response to client
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        #self.send_header('Access-Control-Allow-Origin', RHandler.IP)
        self.end_headers()

    # GET handling
    def do_GET(self):
        self._set_response()

        if MOUSE in self.path:
            self.move_mouse()

        elif CLICK in self.path: self.click()

        elif '__checkbox__' in self.path: RHandler.selection = not RHandler.selection

        # Checks request for HTML
        elif self.req_file(posible = ['/', '/HTML.html', ], variable = 'html', location = 'HTML.html'): pass

        # Checks request for CSS
        elif self.req_file(posible = ['/css/style.css'], variable = 'css', location = 'css\\style.css'): pass

        # Checks request for JS Behavior
        elif self.req_file(posible = ['/js/Behavior.js'], variable = 'js_beh', location = 'js\\Behavior.js'): pass

        # Checks request for JS Keyboard
        elif self.req_file(posible = ['/js/Keyboard.js'], variable = 'js_key', location = 'js\\Keyboard.js'): pass

        # Checks request for JS Mouse.
        elif self.req_file(posible = ['/js/Mouse.js'], variable = 'js_mouse', location = 'js\\Mouse.js'): pass

        elif HOTKEY in self.path:
            hotkey(*self.path[self.path.find(HOTKEY) + len(HOTKEY) : ].split('+'))

        # Checks special/repeat keys
        elif KEYWORD_KEY in self.path:
            pos = self.path.rfind(KEY_SEPARATOR)

            maybe_special = self.path[self.path.find(KEYWORD_KEY) + len(KEYWORD_KEY) : pos]

            # Special key handling
            if maybe_special in ['ctrl', 'alt', 'shift']: self.special_key(pos = pos, maybe_special = maybe_special)

            # Repeat key handling
            else: self.repeat_key(pos = pos)

        # Text input handling
        else: self.just_text()

    # Input parser from URL to usable info
    def path_parser(self):
        return unquote(self.path[1:].replace('favicon.ico', '')).replace(QUESTION, '?')

    # Prevents server from logging output
    def log_message(self, format, *args):
        return

    # Loads file and writes it to client
    def req_file(self, posible : [list[str], tuple[str]], variable : str, location : str):

        # Checks if path is one of the posibilities
        if self.path in posible:

            # Checks if file has already been loaded
            if not len(self.files[variable]):

                # Loads file in its key from self.files
                with open(resource_path(f'.\\templates\\{location}'), 'rt') as file: self.files[variable] = file.read()

            # Writes output to client
            self.wfile.write(self.files[variable].encode('utf-8'))
            return True

        return False

    # Special key handling
    def special_key(self, pos : int, maybe_special : str):

        # Checks if special key comes with extra letter
        try: key_letter = self.path[pos + len(KEY_SEPARATOR)].lower()
        except IndexError: key_letter = False

        # presses and releases (Hot)Key.
        if key_letter: hotkey(maybe_special, key_letter)
        else: key_cont.tap(keyDict[maybe_special])

    # Repeat key handling
    def repeat_key(self, pos : int):

        # Translates repeat key
        key = self.path[self.path.find(KEYWORD_KEY) + len(KEYWORD_KEY) : pos]
        self.path = self.path[pos + len(KEY_SEPARATOR) - 1 : ]

        self.just_text()

        # Taps key

        if RHandler.selection and key in ['up', 'down', 'left', 'right']: hotkey('shift', key)
        else: key_cont.tap(keyDict[key])

    # Text input handling
    def just_text(self):

        # Input parser from path
        word = self.path_parser()

        # If word matches exit sequence, sets running flag to False
        if word == KEYWORD_EXIT: RHandler.running = False

        # If word doesn't match exit sequence, types word
        else: key_cont.type(word)

    def move_mouse(self):

        xpos_path = self.path.find('x')
        ypos_path = self.path.find('y')

        x_rel = float(self.path[xpos_path + 2 : ypos_path]) + .4
        y_rel = float(self.path[ypos_path + 2: ])

        mouse_cont.move(x_rel * DIST, y_rel * DIST)
        # move(x_rel * DIST, y_rel * DIST, _pause=False, duration = .05)

    def click(self):
        pos_button = self.path.find(CLICK)
        mouse_cont.click(mouseDict[self.path[pos_button + len(CLICK) : ]])


