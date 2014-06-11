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

`Preferences` / `Packages Settings` / `SublimeTmpl`



Default key bindings
--------------------

    ctrl+alt+h html
    ctrl+alt+j javascript
    ctrl+alt+c css
    ctrl+alt+p php
    ctrl+alt+r ruby
    ctrl+alt+shift+p python

## Features added

- custom template files

    > put your custom template files in `Packages/User/SublimeTmpl/templates`  
    
- custom template file path

    > your could set your custom template file path in `settings - user` with 
    ``` json
    "custom_path": "[FullPathToYourSublimePackagesPath]/User/[YourCustomTmplName]/templates",
    ```

- `*.tmpl` file support `${date}` variable

    > default "date_format" : "%Y-%m-%d %H:%M:%S" (It is recommended to custom settings in `settings - user`)

- custom variables: `attr`

    > custom the attr variables in settings, example:
    > 
    ``` json
    "attr": {
        "author": "Your Name" ,
        "email": "you@example.org",
        "link": "http://example.org"
        "hello": "word"
    }
``` 

    > The `*.tmpl` file will support `${author}` `${email}` `${link}` `${hello}` variables.


Authors
-------
* **Kairyou** ([Blog](http://www.fantxi.com/blog/) / [GitHub](https://github.com/kairyou))
* **Vfasky** ([Blog](http://vfasky.com) / [GitHub](https://github.com/vfasky))
* **Xu Cheng** ([Github](https://github.com/xu-cheng))

FAQ
---
- SublimeTmpl not work after update the package.

    Please open `Preferences` / `Settings - User`, remove "SublimeTmpl" from `ignored_packages`.

--------------------
Source: [https://github.com/kairyou/SublimeTmpl][0]

Docs: [中文文档](http://www.fantxi.com/blog/archives/sublime-template-engine-sublimetmpl/)


[0]: https://github.com/kairyou/SublimeTmpl
[1]: http://wbond.net/sublime_packages/package_control
