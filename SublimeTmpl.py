# + Python 3 support
# + sublime text 3 support
import os, sublime, sublime_plugin

PACKAGE_NAME = 'SublimeTmpl'
TMLP_DIR = 'templates'
KEY_SYNTAX = 'syntax'
KEY_FILE_EXT = 'extension'

packages_path = sublime.packages_path()
is_gte_st3 = int(sublime.version()[0]) >= 3

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
        print(packages_path)
        if is_gte_st3:
            self.tmpl_path = 'Packages/' + PACKAGE_NAME + '/' + TMLP_DIR + '/' + file_name
            try:
               code = sublime.load_resource(self.tmpl_path)
            except Exception as exception:
                # print(exception)
                isIOError = True
        else:
            self.tmpl_path = os.path.join(PACKAGE_NAME, TMLP_DIR, file_name)
            file = os.path.join(packages_path, self.tmpl_path)
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
