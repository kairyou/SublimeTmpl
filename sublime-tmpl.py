#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + Python 3 support
# + sublime text 3 support

import sublime
import sublime_plugin
# import sys
import os
import glob
import datetime
import zipfile
import re

PACKAGE_NAME = 'SublimeTmpl'
TMLP_DIR = 'templates'
KEY_SYNTAX = 'syntax'
KEY_FILE_EXT = 'extension'

# st3: Installed Packages/xx.sublime-package
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGES_PATH = sublime.packages_path()  # for ST2

# sys.path += [BASE_PATH]
# sys.path.append(BASE_PATH)
# import sys;print(sys.path)

IS_GTE_ST3 = int(sublime.version()[0]) >= 3
DISABLE_KEYMAP = None

class SublimeTmplCommand(sublime_plugin.TextCommand):

    def run(self, edit, type='html'):
        view = self.view
        opts = self.get_settings(type)
        tmpl = self.get_code(type)

        # print('global', DISABLE_KEYMAP, IS_GTE_ST3);
        if DISABLE_KEYMAP:
            return False

        # print(KEY_SYNTAX in opts)
        self.tab = self.creat_tab(view)

        self.set_syntax(opts)
        self.set_code(tmpl)

    def get_settings(self, type=None):
        settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')

        if not type:
            return settings

        # print(settings.get('html')['syntax'])
        opts = settings.get(type, [])
        # print(opts)
        return opts

    def open_file(self, path, mode='r'):
        fp = open(path, mode)
        code = fp.read()
        fp.close()
        return code

    def get_code(self, type):
        code = ''
        file_name = "%s.tmpl" % type
        isIOError = False

        if IS_GTE_ST3:
            tmpl_dir = 'Packages/' + PACKAGE_NAME + '/' + TMLP_DIR + '/'
            user_tmpl_dir = 'Packages/User/' + \
                PACKAGE_NAME + '/' + TMLP_DIR + '/'
            # tmpl_dir = os.path.join('Packages', PACKAGE_NAME , TMLP_DIR)
        else:
            tmpl_dir = os.path.join(PACKAGES_PATH, PACKAGE_NAME, TMLP_DIR)
            user_tmpl_dir = os.path.join(
                PACKAGES_PATH, 'User', PACKAGE_NAME, TMLP_DIR)

        self.user_tmpl_path = os.path.join(user_tmpl_dir, file_name)
        self.tmpl_path = os.path.join(tmpl_dir, file_name)

        if IS_GTE_ST3:
            try:
                code = sublime.load_resource(self.user_tmpl_path)
            except IOError:
                try:
                    code = sublime.load_resource(self.tmpl_path)
                except IOError:
                    isIOError = True
        else:
            if os.path.isfile(self.user_tmpl_path):
                code = self.open_file(self.user_tmpl_path)
            elif os.path.isfile(self.tmpl_path):
                code = self.open_file(self.tmpl_path)
            else:
                isIOError = True

        # print(self.tmpl_path)
        if isIOError:
            sublime.message_dialog('[Warning] No such file: ' + self.tmpl_path
                                   + ' or ' + self.user_tmpl_path)

        return self.format_tag(code)

    def format_tag(self, code):
        code = code.replace('\r', '') # replace \r\n -> \n
        # format
        settings = self.get_settings()
        format = settings.get('date_format', '%Y-%m-%d')
        date = datetime.datetime.now().strftime(format)
        if not IS_GTE_ST3:
            code = code.decode('utf8') # for st2 && Chinese characters
        code = code.replace('${date}', date)

        attr = settings.get('attr', {})
        for key in attr:
            code = code.replace('${%s}' % key, attr.get(key, ''))
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
        # syntax = self.view.settings().get('syntax') # from current file
        syntax = opts[KEY_SYNTAX] if KEY_SYNTAX in opts else ''
        # print(syntax) # tab.set_syntax_file('Packages/Diff/Diff.tmLanguage')
        v.set_syntax_file(syntax)

        # print(opts[KEY_FILE_EXT])
        if KEY_FILE_EXT in opts:
            v.settings().set('default_extension', opts[KEY_FILE_EXT])

class SublimeTmplEventListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')
        disable_keymap_actions = settings.get('disable_keymap_actions', '')
        # print ("key1: %s, %s" % (key, disable_keymap_actions))
        global DISABLE_KEYMAP
        DISABLE_KEYMAP = False;
        if not key.startswith('sublime_tmpl.'):
            return None
        if not disable_keymap_actions: # no disabled actions
            return True
        elif disable_keymap_actions == 'all' or disable_keymap_actions == True: # disable all actions
            DISABLE_KEYMAP = True;
            return False
        prefix, name = key.split('.')
        ret = name not in re.split(r'\s*,\s*', disable_keymap_actions.strip())
        # print(name, ret)
        DISABLE_KEYMAP = True if not ret else False;
        return ret

def plugin_loaded():  # for ST3 >= 3016
    # global PACKAGES_PATH
    PACKAGES_PATH = sublime.packages_path()
    TARGET_PATH = os.path.join(PACKAGES_PATH, PACKAGE_NAME)
    # print(BASE_PATH, os.path.dirname(BASE_PATH))
    # print(TARGET_PATH)

    # auto create custom_path
    custom_path = os.path.join(PACKAGES_PATH, 'User', PACKAGE_NAME, TMLP_DIR)
    # print(custom_path, os.path.isdir(custom_path))
    if not os.path.isdir(custom_path):
        os.makedirs(custom_path)

    # first run
    if not os.path.isdir(TARGET_PATH):
        os.makedirs(os.path.join(TARGET_PATH, TMLP_DIR))
        # copy user files
        tmpl_dir = TMLP_DIR + '/'
        file_list = [
            'Default.sublime-commands', 'Main.sublime-menu',
            # if don't copy .py, ST3 throw: ImportError: No module named
            'sublime-tmpl.py',
            'README.md',
            tmpl_dir + 'css.tmpl', tmpl_dir + 'html.tmpl',
            tmpl_dir + 'js.tmpl', tmpl_dir + 'php.tmpl',
            tmpl_dir + 'python.tmpl', tmpl_dir + 'ruby.tmpl',
            tmpl_dir + 'xml.tmpl'
        ]
        try:
            extract_zip_resource(BASE_PATH, file_list, TARGET_PATH)
        except Exception as e:
            print(e)

    # old: *.user.tmpl compatible fix
    files = glob.iglob(os.path.join(os.path.join(TARGET_PATH, TMLP_DIR), '*.user.tmpl'))
    for file in files:
        filename = os.path.basename(file).replace('.user.tmpl', '.tmpl')
        # print(file, '=>', os.path.join(custom_path, filename));
        os.rename(file, os.path.join(custom_path, filename))

    # old: settings-custom_path compatible fix
    settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')
    old_custom_path = settings.get('custom_path', '')
    if old_custom_path and os.path.isdir(old_custom_path):
        # print(old_custom_path)
        files = glob.iglob(os.path.join(old_custom_path, '*.tmpl'))
        for file in files:
            filename = os.path.basename(file).replace('.user.tmpl', '.tmpl')
            # print(file, '=>', os.path.join(custom_path, filename))
            os.rename(file, os.path.join(custom_path, filename))

if not IS_GTE_ST3:
    sublime.set_timeout(plugin_loaded, 0)

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
