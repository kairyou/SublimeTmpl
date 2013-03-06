# + Python 3 support
# + sublime text 3 support

import sublime, sublime_plugin
import sys, os

import zipfile

PACKAGE_NAME = 'SublimeTmpl'
TMLP_DIR = 'templates'
KEY_SYNTAX = 'syntax'
KEY_FILE_EXT = 'extension'

BASE_PATH = os.path.abspath(os.path.dirname(__file__)) #Installed Packages/xx.sublime-package
PACKAGES_PATH = sublime.packages_path() # for ST2

# sys.path += [BASE_PATH]
# sys.path.append(BASE_PATH)
# import sys;print(sys.path)

IS_GTE_ST3 = int(sublime.version()[0]) >= 3

class SublimeTmplCommand(sublime_plugin.TextCommand):

    def run(self, edit, type = 'html'):
        view = self.view
        opts = self.get_settings(type)
        tmpl = self.get_code(type)

        # print(KEY_SYNTAX in opts)
        self.tab = self.creat_tab(view)

        self.set_syntax(opts)
        self.set_code(tmpl)

    def get_settings(self, type):
        settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')
        # print(settings.get('html')['syntax'])
        opts = settings.get(type, [])
        # print(opts)
        return opts

    def get_code(self, type):
        code = ''
        file_name = type + '.tmpl'
        isIOError = False
        # print(PACKAGES_PATH)
        if IS_GTE_ST3:
            self.tmpl_path = 'Packages/' + PACKAGE_NAME + '/' + TMLP_DIR + '/' + file_name
            try:
               code = sublime.load_resource(self.tmpl_path)
            except Exception as exception:
                # print(exception)
                isIOError = True
        else:
            self.tmpl_path = os.path.join(PACKAGE_NAME, TMLP_DIR, file_name)
            file = os.path.join(PACKAGES_PATH, self.tmpl_path)
            if not os.path.exists(file):
                isIOError = True
            else:
                fp = open(file, 'r')
                code = fp.read()
                fp.close()
        # print(self.tmpl_path)
        if isIOError:
            sublime.message_dialog('[Warning] No such file: ' + self.tmpl_path)
        return code

    def creat_tab(self, view):
        win = view.window()
        tab = win.new_file()
        return tab

    def set_code(self, code):
        tab = self.tab
        # tab.set_name('untitled.' + self.type)
        # insert codes
        tab.run_command('insert_snippet', {'contents': code})

    def set_syntax(self, opts):
        v = self.tab
        # syntax = self.view.settings().get('syntax') # syntax from current file
        syntax = opts[KEY_SYNTAX] if KEY_SYNTAX in opts else ''
        # print(syntax) # tab.set_syntax_file('Packages/Diff/Diff.tmLanguage')
        v.set_syntax_file(syntax)

        # print(opts[KEY_FILE_EXT])
        if KEY_FILE_EXT in opts:
            v.settings().set('default_extension', opts[KEY_FILE_EXT])

# for ST3 >= 3016
def plugin_loaded():
    # global PACKAGES_PATH
    PACKAGES_PATH = sublime.packages_path()
    TARGET_PATH = os.path.join(PACKAGES_PATH, PACKAGE_NAME)
    # print(BASE_PATH, os.path.dirname(BASE_PATH))
    # print(TARGET_PATH)

    # first run
    if not os.path.isdir(TARGET_PATH):
        os.makedirs(os.path.join(TARGET_PATH, TMLP_DIR))
        # copy user files
        tmpl_dir = TMLP_DIR + '/'
        file_list = [
        'Default.sublime-commands', 'Main.sublime-menu',
        # if don't copy .py, ST3 throw an exception: ImportError: No module named
        'sublime-tmpl.py', 
        'README.md',
        tmpl_dir + 'css.tmpl', tmpl_dir + 'html.tmpl', tmpl_dir + 'js.tmpl',
        tmpl_dir + 'php.tmpl', tmpl_dir + 'python.tmpl', tmpl_dir + 'ruby.tmpl',
        tmpl_dir + 'xml.tmpl'
        ]
        try:
            extract_zip_resource(BASE_PATH, file_list, TARGET_PATH)
        except Exception as e:
            print(e)

def extract_zip_resource(path_to_zip, file_list, extract_dir=None):
    if extract_dir is None:
        return
    # print(extract_dir)
    if os.path.exists(path_to_zip):
        z = zipfile.ZipFile(path_to_zip, 'r')
        for f in z.namelist():
            # if f.endswith('.tmpl'):
            if f in file_list:
                # print(f)
                z.extract(f, extract_dir)
        z.close()