import os, sublime, sublime_plugin

PACKAGE_NAME = 'SublimeTmpl'
TMLP_DIR = 'templates'
KEY_SYNTAX = 'syntax'
KEY_FILE_EXT = 'extension'
PACKAGES_PATH = sublime.packages_path()

class SublimeTmplCommand(sublime_plugin.TextCommand):


    def run(self, edit, type = 'html'):
        view = self.view
        
        self.tmpl_path = os.path.join(PACKAGE_NAME, TMLP_DIR, type + '.tmpl')
        file = os.path.join(PACKAGES_PATH, self.tmpl_path)
        # print file

        opts = self.get_settings(type)
        # print KEY_SYNTAX in data
        
        self.tab = self.creat_tab(view)

        tmpl = self.get_code(file)
        self.set_syntax(opts)
        self.set_code(tmpl)

    def get_settings(self, type):
        settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')
        # print settings.get('html')['syntax']
        opts = settings.get(type, [])
        # print opts
        return opts

    def get_code(self, file):
        code = ''
        # print os.path.exists(file)
        if not os.path.exists(file):
            # error_message
            sublime.message_dialog('[Warning] No such file: ' + self.tmpl_path)
        else:
            fp = open(file, 'r')
            code = fp.read()
            fp.close()
            # print code
        return code

    def creat_tab(self, view):
        win = view.window()
        tab = win.new_file()
        return tab

    def set_code(self, code):
        tab = self.tab

        # 'untitled.' + type
        # tab.set_name('')
        tab.set_name('')

        # set syntax from current file
        # syntax = view.settings().get('syntax')
        # print syntax
        # tab.set_syntax_file('Packages/Diff/Diff.tmLanguage')
        # tab.set_syntax_file(syntax)

        # insert codes
        edit = tab.begin_edit()
        # tab.insert(edit, 0, code)
        tab.run_command("insert_snippet", {'contents': code})
        tab.end_edit(edit)

    def set_syntax(self, opts):
        v = self.tab
        # set syntax from current file
        # syntax = self.view.settings().get('syntax')

        # print opts[KEY_FILE_EXT]
        # ext = opts[KEY_FILE_EXT] if KEY_FILE_EXT in opts else 'txt'
        # v.settings().set('default_extension', ext)
        if KEY_FILE_EXT in opts:
            v.settings().set('default_extension', opts[KEY_FILE_EXT])


        syntax = opts[KEY_SYNTAX] if KEY_SYNTAX in opts else ''
        # print syntax
        v.set_syntax_file(syntax)
