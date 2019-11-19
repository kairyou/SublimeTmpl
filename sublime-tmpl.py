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
import shutil

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

    def run(self, edit, type='html', paths = None):
        view = self.view

        if type == 'project':
            # need to present project-specific templates for user to select

            projectFolder = self.get_project_template_folder()
            if not projectFolder:
                sublime.message_dialog('No "template_folder" specified in current project file')
                return False

            self.project_templates = []
            for dirpath, dirnames, filenames in os.walk(projectFolder):
                # for dirname in dirnames:
                #     self.project_templates.append(dirname)
                for filename in filenames:
                    if filename.endswith(".tmpl"):
                        self.project_templates.append((dirpath, os.path.splitext(filename)[0]))
            
            options = []
            for (path, name) in self.project_templates:
                options.append("Template: {}".format(name))

            if not options:
                sublime.message_dialog('No templates found in current project template folder {0}'.format(projectFolder))
                return False

            self.view.window().show_quick_panel(
                options,
                selected_index=0,
                on_select=self.run_project_template,
                on_highlight=None,
            )

            return

        opts = self.get_settings(type)
        tmpl = self.get_code(type)

        # print('global', DISABLE_KEYMAP, IS_GTE_ST3);
        if DISABLE_KEYMAP:
            return False

        # print(KEY_SYNTAX in opts)
        self.tab = self.creat_tab(view, paths)

        self.set_syntax(opts)
        # sublime.set_timeout(lambda: self.set_syntax(opts), 1000)
        self.set_code(tmpl)

    def run_project_template(self, index):
        self.view.run_command('sublime_tmpl',
                                    args={'type': self.project_templates[index][1]})

    def get_settings(self, type=None):
        settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')

        if not type:
            return settings

        # print(settings.get('html')['syntax'])
        opts = settings.get(type, [])
        # print(opts)
        return opts

    def open_file(self, path, mode='r'):
        with open(path, mode) as fp:
            code = fp.read()
        return code

    @staticmethod
    def is_resource_path(path):
        """ Check if an absolute path points to an ST3 resource folder """
        if IS_GTE_ST3:
            return os.path.commonprefix([path, sublime.packages_path()]) == sublime.packages_path()
        else:
            return False   # doesn't apply for ST2

    @staticmethod
    def format_as_resource_path(path):
        """ Convert an absolute path to an ST3 resource path """
        return os.path.join('Packages', os.path.relpath(path, sublime.packages_path()))

    def get_project_template_folder(self):
        """ Get project template folder (if one is set) """
        project_tmpl_dir = None   # only available for ST3 - per-project template folders

        if IS_GTE_ST3:
            project_tmpl_dir = self.view.window().project_data().get('template_folder', None)

        return project_tmpl_dir

    def get_template_folders(self):
        """ Returns list of paths expected to contain templates.
            Paths are absolute, additional conversion needed for ST3 resource paths """
        project_tmpl_dir = self.get_project_template_folder()
        tmpl_dir = os.path.join(PACKAGES_PATH, PACKAGE_NAME, TMLP_DIR)
        user_tmpl_dir = os.path.join(PACKAGES_PATH, 'User', PACKAGE_NAME, TMLP_DIR)

        if project_tmpl_dir is not None:
           project_tmpl_dir = os.path.abspath(project_tmpl_dir)

        paths = []

        # inserted in order we want to search (more specific -> more general)
        if project_tmpl_dir is not None and os.path.exists(project_tmpl_dir):
            paths.append(project_tmpl_dir)
        if os.path.exists(user_tmpl_dir):
            paths.append(user_tmpl_dir)
        if os.path.exists(tmpl_dir):
            paths.append(tmpl_dir)
        
        return paths

    def get_code(self, type):
        code = ''
        file_name = "%s.tmpl" % type
        templateFound = False

        paths = self.get_template_folders()
        print(sublime.packages_path())
        print(sublime.installed_packages_path())

        for path in paths:
            fullpath = os.path.join(path, file_name)
            if self.is_resource_path(fullpath):
                try:
                    fullpath = self.format_as_resource_path(fullpath)
                    code = sublime.load_resource(fullpath)
                    templateFound = True
                except IOError:
                    pass  # try the next folder
            else:
                if os.path.isfile(fullpath):
                    code = self.open_file(fullpath)
                    templateFound = True

            if templateFound:
                break

        if not templateFound:
            sublime.message_dialog('[Warning] No such file {0} found in paths {1}: '.format(
                file_name, paths))

        return self.format_tag(code)

    def format_tag(self, code):
        win = self.view.window()
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

        # print(hasattr(win, 'extract_variables'))
        # print(win.extract_variables(), win.project_data())
        if settings.get('enable_project_variables', False) and hasattr(win, 'extract_variables'):
            variables = win.extract_variables()
            for key in ['project_base_name', 'project_path', 'platform']:
                code = code.replace('${%s}' % key, variables.get(key, ''))

        # keep ${var..}
        code = re.sub(r"(?<!\\)\${(?!\d)", '\${', code)
        return code

    def creat_tab(self, view, paths = None):
        if paths is None:
            paths = [None]

        win = view.window()
        # tab = win.open_file('/tmp/123')
        tab = win.new_file()
        # tab.set_name('untitled')
        active = win.active_view()
        active.settings().set('default_dir', paths[0])
        return tab

    def set_code(self, code):
        tab = self.tab
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

class SublimeTmplReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, old, new):
        # print('tmpl_replace', old, new)
        region = sublime.Region(0, self.view.size())
        if region.empty() or not old or not new:
            return
        s = self.view.substr(region)
        s = s.replace(old, new)
        self.view.replace(edit, region, s)

class SublimeTmplEventListener(sublime_plugin.EventListener):
    def __init__(self):
        self.unsaved_ids = {}
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
    def on_activated(self, view):
        if view.file_name():
            return
        settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')
        if settings.get('enable_file_variables_on_save', False):
            self.unsaved_ids[view.id()] = True
        # print('on_activated', self.unsaved_ids, view.id(), view.file_name())
    def on_pre_save(self, view):
        if not view.id() in self.unsaved_ids:
            return
        settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')
        if settings.get('enable_file_variables_on_save', False):
            filepath = view.file_name()
            filename = os.path.basename(filepath)
            view.run_command('sublime_tmpl_replace', {'old': '${saved_filepath}', 'new': filepath})
            view.run_command('sublime_tmpl_replace', {'old': '${saved_filename}', 'new': filename})
            del self.unsaved_ids[view.id()]

def plugin_loaded():  # for ST3 >= 3016
    # global PACKAGES_PATH
    PACKAGES_PATH = sublime.packages_path()
    TARGET_PATH = os.path.join(PACKAGES_PATH, PACKAGE_NAME)
    # print(BASE_PATH, os.path.dirname(BASE_PATH), TARGET_PATH)

    # auto create custom_path
    custom_path = os.path.join(PACKAGES_PATH, 'User', PACKAGE_NAME, TMLP_DIR)
    # print(custom_path, os.path.isdir(custom_path))
    not_existed = not os.path.isdir(custom_path)
    if not_existed:
        os.makedirs(custom_path)

        files = glob.iglob(os.path.join(BASE_PATH, TMLP_DIR, '*.tmpl'))
        for file in files:
            dst_file = os.path.join(custom_path, os.path.basename(file))
            if not os.path.exists(dst_file):
                shutil.copy(file, dst_file)


    # first run (https://git.io/vKMIS, does not need extract files)
    if not os.path.isdir(TARGET_PATH):
        os.makedirs(os.path.join(TARGET_PATH, TMLP_DIR))
        # copy user files
        tmpl_dir = TMLP_DIR + '/'
        file_list = [
            'Default.sublime-commands', 'Main.sublime-menu',
            # if don't copy .py, ST3 throw: ImportError: No module named # fix: restart sublime
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
        with zipfile.ZipFile(path_to_zip, 'r') as z:
            for f in z.namelist():
                # if f.endswith('.tmpl'):
                if f in file_list:
                    # print(f)
                    z.extract(f, extract_dir)
