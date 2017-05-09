SublimeTmpl
===========

A Sublime Text 2/3 plugin for create file from templates.

Installation
------------

**Github**

Go to the "Packages" directory (`Preferences` / `Browse Packages`). Then clone this repository:

    $ git clone https://github.com/kairyou/SublimeTmpl.git

**Package Control**

Install [Package Control][1]. Then `Package Control: Install Package`, look for `SublimeTmpl` / `tmpl` and install it.

Usage
-----

- Creat file with menu
   `File - New File (SublimeTmpl)`

- Creat file with command
   use `cmd+shift+p` then look for `tmpl:`

Settings
--------

Default Settings: `Preferences` > `Packages Settings` > `SublimeTmpl` > `Settings - Default`

Custom settings (**Recommend*): `Preferences` > `Package Settings` > `SublimeTmpl` > `Settings - User`

Default template files: `Packages/SublimeTmpl/templates`

Custom template files (**Recommend*): `Packages/User/SublimeTmpl/templates/`


Default key bindings
--------------------

    ctrl+alt+h html
    ctrl+alt+j javascript
    ctrl+alt+c css
    ctrl+alt+p php
    ctrl+alt+r ruby
    ctrl+alt+shift+p python

**Disable shortcuts**

If you’re unhappy with default keymap, you can disable keyboard shortcuts with `disable_keymap_actions` preference of `SublimeTmpl.sublime-settings`.

Use a comma-separated list of action names which default keyboard shortcuts should be disabled. For example, if you want to disable creat `html` and `css` shortcuts, your must set the following value:

    "disabled_keymap_actions": "html, css"

To disable all default shortcuts, set value to `all`.


## Features added

- custom template files

    > put your custom template files in `Packages/User/SublimeTmpl/templates`  

- `*.tmpl` file support `${date}` variable

    > default "date_format" : "%Y-%m-%d %H:%M:%S" .

- `*.tmpl` file support `${saved_filename}`, `${saved_filepath}` on save file

    > Enable: `SublimeTmpl > settings - user` add `"enable_file_variables_on_save": true,`

- `*.tmpl` file support `${project_base_name}`, `${project_path}` and `${platform}`

    NOTE: This will only work with SublimeText 3.0 or above.

    > Enable: `SublimeTmpl > settings - user` add `"enable_project_variables": true,`


It is recommended that you put your own custom settings in `settings - user`.  Please see note below in "*Detailed Instructions for Sublime Newbies"

- custom variables: `attr`

    > custom the attr variables in settings, example:
    >
 ``` json
    "attr": {
        "author": "Your Name" ,
        "email": "you@example.org",
        "link": "http://example.org",
        "hello": "word"
    }
```

    > The `*.tmpl` file will support `${author}` `${email}` `${link}` `${hello}` variables.

*Detailed Instructions for Sublime Newbies
-----------------------------------------

Sublime Text keeps settings in bunch of files in a folder. For example, OS X, it is located at

```/Users/yourusername/Library/Application Support/Sublime Text 3/Packages```

You can navigate to it easily by using the following menu item in Sublime, for example: `Sublime Text>Preferences>Browse Packages`

Now go to `Packages\SublimeTmpl` folder and open the file SublimeTmpl.sublime-settings.  Save the file with the same file name under `Packages\User`. Delete everything except the variables that are custom to you. By the time you are finished, the file might look as simple as this (JSON format):
```
{
    "attr": {
        "author": "Chuck Norris" ,
        "email": "chuck@kickbutt.com",
    }
}
```

If you don't want the  `"link"` and `"hello"` variables to show up, you should copy the (for example) python.tmpl file to `Packages/User/SublimeTmpl/templates` and remove those elements from it.  


Contributors
-------
- [View Contributors](https://github.com/kairyou/SublimeTmpl/graphs/contributors)

### Donate
<span class="badge-paypal"><a href="https://www.paypal.me/kairyou" title="Donate to this project using Paypal"><img src="https://img.shields.io/badge/paypal-donate-yellow.svg" alt="PayPal donate button" /></a></span>

FAQ
---
- SublimeTmpl not work after update the package.

    Please open `Preferences` / `Settings - User`, remove "SublimeTmpl" from `ignored_packages`.

--------------------
Source: [https://github.com/kairyou/SublimeTmpl][0]

Docs: [中文文档](http://www.fantxi.com/blog/archives/sublime-template-engine-sublimetmpl/)


[0]: https://github.com/kairyou/SublimeTmpl
[1]: https://packagecontrol.io
