SublimeTmpl
===========

A Sublime Text 2/3 plugin for create file from templates.

Installation
------------

**Github**

Go to the "Packages" directory (`Preferences` / `Browse Packages`). Then clone this repository:

    $ git clone https://github.com/kairyou/SublimeTmpl.git

**Package Control**

- Install [Package Control][1]. Then `Package Control: Install Package`

- look for `SublimeTmpl` and install it.

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

## 新增特性：

### 支持用户自定义模板

> 如: `python.tmpl` 的自定义模板为 `python.user.tmpl`

### 模板支持 `${date}` 变量

> 用于显示当前时间

### 模板支持自定义 attr

> 在配置文件中加入或更改对应的attr,就能在模板中调用

如定义以下标签：

``` json
"attr": {
    "author": "vfasky" ,
    "email": "vfasky@gmail.com",
    "link": "http://vfasky.com",
    "hello": "word"
}
``` 

就能在模板中使用 `${author}` `${email}` `${link}` `${hello}` 变量



Source: [https://github.com/kairyou/SublimeTmpl][0]

Docs: [中文文档][4]

Authors: [Kairyou][3]

 [0]: https://github.com/kairyou/SublimeTmpl
 [1]: http://wbond.net/sublime_packages/package_control
 [3]: http://www.fantxi.com/blog/
 [4]: http://www.fantxi.com/blog/archives/sublime-template-engine-sublimetmpl/

