*This repository was created for the xontrib that xonsh [contains by default](https://github.com/xonsh/xonsh/tree/main/xontrib).* 

# xontrib-abbrevs

Command abbreviations.

This expands input words from `abbrevs` dictionary as you type.

Adds ``abbrevs`` dictionary to hold user-defined "command abbreviations.

The dictionary is searched as you type the matching words are replaced
at the command line by the corresponding dictionary contents once you hit
'Space' or 'Return' key.

For instance a frequently used command such as ``git status`` can be abbreviated to ``gst`` as follows::
```xsh
xontrib load abbrevs
abbrevs['gst'] = 'git status'
gst # Once you hit <space> or <return> 'gst' gets expanded to 'git status'.
```
one can set a callback function that receives current buffer and word to customize the expanded word based on context
```xsh
abbrevs['ps'] = lambda buffer, word: "procs" if buffer.text.startswith(word) else word
```
It is also possible to set the cursor position after expansion with,
```xsh
abbrevs['gp'] = "git push <edit> --force"
```
