"""Regression tests using a minimal Sublime API stub; run with unittest discover."""
import importlib.util
import json
import ntpath
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sublime = types.ModuleType('sublime')
sublime.Settings = type('Settings', (), {})
sublime.version = lambda: '4200'
sublime.packages_path = lambda: ''
sublime.set_timeout = mock.Mock()
sublime.message_dialog = mock.Mock()
sublime.load_resource = mock.Mock(side_effect=IOError('Missing resource'))
sublime_plugin = types.ModuleType('sublime_plugin')
sublime_plugin.TextCommand = type('TextCommand', (), {})
sublime_plugin.WindowCommand = type('WindowCommand', (), {})
sublime_plugin.EventListener = type('EventListener', (), {})

with mock.patch.dict(sys.modules, sublime=sublime, sublime_plugin=sublime_plugin):
    spec = importlib.util.spec_from_file_location('sublime_tmpl', ROOT / 'sublime-tmpl.py')
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)


class PluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.packages = Path(self.temp.name) / 'Packages'
        self.packages.mkdir()
        self.command = plugin.SublimeTmplCommand()
        self.command.view = mock.Mock()
        self.command.get_project_template_folder = lambda: None
        self.command.get_template_extension = lambda: '.tmpl'
        self.settings = {
            'template_replace_pattern': '${%s}',
            'attr': {'author': 'Ada', 'description': 'A new Python script'}
        }
        patches = [
            mock.patch.object(plugin, 'IS_GTE_ST3', True),
            mock.patch.object(plugin, 'get_settings', return_value=self.settings),
            mock.patch.object(sublime, 'packages_path', return_value=str(self.packages)),
            mock.patch.object(sublime, 'load_resource', side_effect=IOError('Missing resource')),
            mock.patch.object(sublime, 'message_dialog'),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def write_template(self, folder, text):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'python_note.tmpl').write_text(text, encoding='utf-8')

    def test_windows_resource_paths_use_forward_slashes(self):
        with mock.patch.object(plugin.os, 'path', ntpath), \
                mock.patch.object(plugin.os, 'sep', '\\'), \
                mock.patch.object(sublime, 'packages_path', return_value=r'C:\Data\Packages'):
            self.assertEqual(
                self.command.format_as_resource_path(r'C:\Data\Packages\SublimeTmpl\templates\python.tmpl'),
                'Packages/SublimeTmpl/templates/python.tmpl'
            )

    def test_bundled_template_loads_without_extracted_directory(self):
        sublime.load_resource.side_effect = None
        sublime.load_resource.return_value = '# ${author}\n$0'
        self.assertEqual(self.command.get_code('python_note'), '# Ada\n$0')
        sublime.load_resource.assert_called_once_with(
            'Packages/SublimeTmpl/templates/python_note.tmpl'
        )

    def test_project_then_user_then_default_template_precedence(self):
        project = Path(self.temp.name) / 'project-templates'
        user = self.packages / 'User' / 'SublimeTmpl' / 'templates'
        default = self.packages / 'SublimeTmpl' / 'templates'
        for folder, text in [(project, 'project'), (user, 'user'), (default, 'default')]:
            self.write_template(folder, text)
        self.command.get_project_template_folder = lambda: str(project)
        self.assertEqual(self.command.get_code('python_note'), 'project')
        sublime.load_resource.assert_not_called()
        (project / 'python_note.tmpl').unlink()
        self.assertEqual(self.command.get_code('python_note'), 'user')
        sublime.load_resource.assert_not_called()
        (user / 'python_note.tmpl').unlink()
        self.assertEqual(self.command.get_code('python_note'), 'default')
        sublime.load_resource.assert_called_once_with(
            'Packages/User/SublimeTmpl/templates/python_note.tmpl'
        )

    def test_documented_custom_template_and_unicode_variables(self):
        self.write_template(
            self.packages / 'User' / 'SublimeTmpl' / 'templates',
            '# ${description}\n# Author: ${author}\n# 中文\n$0'
        )
        self.assertEqual(
            self.command.get_code('python_note'),
            '# A new Python script\n# Author: Ada\n# 中文\n$0'
        )

    def test_create_template_sets_syntax_extension_and_expands_variables(self):
        self.write_template(
            self.packages / 'User' / 'SublimeTmpl' / 'templates',
            '# ${description}\n# Author: ${author}\n$0'
        )
        opts = {'syntax': 'Packages/Python/Python.tmLanguage', 'extension': 'py'}
        sublime.load_resource.side_effect = None
        sublime.load_resource.return_value = '%YAML 1.2'
        with mock.patch.object(plugin, 'get_settings', side_effect=lambda view, type=None:
                               opts if type else self.settings):
            self.command.run(None, type='python_note')
        tab = self.command.view.window().new_file.return_value
        tab.set_syntax_file.assert_called_once_with('Packages/Python/Python.sublime-syntax')
        tab.settings().set.assert_called_once_with('default_extension', 'py')
        tab.run_command.assert_called_once_with('insert_snippet', {
            'contents': '# A new Python script\n# Author: Ada\n$0'
        })

    def test_missing_template_reports_warning(self):
        self.assertEqual(self.command.get_code('missing'), '')
        sublime.message_dialog.assert_called_once()

    def test_modern_syntax_is_selected_when_available(self):
        self.command.tab = mock.Mock()
        sublime.load_resource.side_effect = None
        sublime.load_resource.return_value = '%YAML 1.2'
        self.command.set_syntax({'syntax': 'Packages/Python/Python.tmLanguage', 'extension': 'py'})
        self.command.tab.set_syntax_file.assert_called_once_with('Packages/Python/Python.sublime-syntax')
        self.command.tab.settings().set.assert_called_once_with('default_extension', 'py')

    def test_old_st3_syntax_falls_back_to_configured_path(self):
        self.command.tab = mock.Mock()
        self.command.set_syntax({'syntax': 'Packages/Python/Python.tmLanguage'})
        self.command.tab.set_syntax_file.assert_called_once_with('Packages/Python/Python.tmLanguage')

    def test_st2_keeps_legacy_syntax_without_resource_api(self):
        self.command.tab = mock.Mock()
        with mock.patch.object(plugin, 'IS_GTE_ST3', False):
            self.command.set_syntax({'syntax': 'Packages/Python/Python.tmLanguage'})
        self.command.tab.set_syntax_file.assert_called_once_with('Packages/Python/Python.tmLanguage')
        sublime.load_resource.assert_not_called()

    def test_explicit_custom_syntax_is_preserved(self):
        self.command.tab = mock.Mock()
        self.command.set_syntax({'syntax': 'Packages/Julia/Julia.sublime-syntax'})
        self.command.tab.set_syntax_file.assert_called_once_with('Packages/Julia/Julia.sublime-syntax')
        sublime.load_resource.assert_not_called()

    def test_unknown_snippet_variables_are_preserved(self):
        self.assertEqual(
            self.command.format_tag('${author} ${unknown} ${1:placeholder} $0'),
            r'Ada \${unknown} ${1:placeholder} $0'
        )

    def test_default_keymap_opens_from_package_for_each_platform(self):
        command = plugin.SublimeTmplOpenKeymapCommand()
        for platform, filename in [('windows', 'Windows'), ('linux', 'Linux'), ('osx', 'OSX')]:
            with self.subTest(platform=platform), \
                    mock.patch.object(sublime, 'platform', return_value=platform, create=True):
                command.window = mock.Mock()
                command.run()
                command.window.run_command.assert_called_once_with('open_resource', {
                    'resource': 'Packages/SublimeTmpl/Default (%s).sublime-keymap' % filename
                })
                self.assertTrue((ROOT / ('Default (%s).sublime-keymap' % filename)).is_file())

    def test_st2_default_keymap_opens_from_disk(self):
        command = plugin.SublimeTmplOpenKeymapCommand()
        command.window = mock.Mock()
        with mock.patch.object(plugin, 'IS_GTE_ST3', False), \
                mock.patch.object(sublime, 'platform', return_value='windows', create=True):
            command.run()
        command.window.open_file.assert_called_once_with(
            str(self.packages / 'SublimeTmpl' / 'Default (Windows).sublime-keymap')
        )
        command.window.run_command.assert_not_called()

    def test_default_keymap_menu_uses_package_command(self):
        menu = json.loads((ROOT / 'Main.sublime-menu').read_text(encoding='utf-8'))
        def find_entries(entries):
            for entry in entries:
                if entry.get('caption') == 'Key Bindings – Default':
                    yield entry
                for child in find_entries(entry.get('children', [])):
                    yield child
        self.assertEqual(list(find_entries(menu)), [{
            'command': 'sublime_tmpl_open_keymap', 'caption': 'Key Bindings – Default'
        }])


if __name__ == '__main__':
    unittest.main()
