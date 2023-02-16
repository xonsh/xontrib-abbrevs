<p align="center">
Expands input words as you type in xonsh shell.
</p>

<p align="center">
If you like the idea click ⭐ on the repo and <a href="https://twitter.com/intent/tweet?text=Nice%20xontrib%20for%20the%20xonsh%20shell!&url=https://github.com/xonsh/xontrib-abbrevs" target="_blank">tweet</a>.
</p>


## Installation

To install use pip:

```bash
xpip install xontrib-abbrevs
# or: xpip install -U git+https://github.com/xonsh/xontrib-abbrevs
```

## Usage

This expands input words from `abbrevs` dictionary as you type.
Adds ``abbrevs`` dictionary to hold user-defined "command abbreviations.
The dictionary is searched as you type the matching words are replaced
at the command line by the corresponding dictionary contents once you hit
'Space' or 'Return' key.

For instance a frequently used command such as ``git status`` can be abbreviated to ``gst`` as follows:

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

## Credits

This package was created with [xontrib template](https://github.com/xonsh/xontrib-template).
