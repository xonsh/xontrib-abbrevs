import builtins
import typing as tp

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters import IsMultiline, completion_is_selected
from prompt_toolkit.keys import Keys
from xonsh.built_ins import DynamicAccessProxy, XonshSession
from xonsh.tools import check_for_partial_string

__all__ = ()


if tp.TYPE_CHECKING:

    class AbbrCallType(tp.Protocol):
        def __call__(self, word: str, buffer: Buffer) -> str:
            ...

    AbbrValType = tp.Union[str, AbbrCallType]

abbrevs: "dict[str, AbbrValType]" = dict()


class _LastExpanded(tp.NamedTuple):
    word: str
    expanded: str


class Abbreviation:
    """A container class to handle state related to abbreviating keywords"""

    last_expanded: tp.Optional[_LastExpanded] = None

    def expand(self, buffer: Buffer) -> bool:
        """expand the given abbr text. Return true if cursor position changed."""
        if not abbrevs:
            return False
        document = buffer.document
        word = document.get_word_before_cursor(WORD=True)
        if word in abbrevs.keys():
            partial = document.text[: document.cursor_position]
            startix, endix, quote = check_for_partial_string(partial)
            if startix is not None and endix is None:
                return False
            text = get_abbreviated(word, buffer)

            buffer.delete_before_cursor(count=len(word))
            buffer.insert_text(text)

            self.last_expanded = _LastExpanded(word, text)
            if EDIT_SYMBOL in text:
                set_cursor_position(buffer, text)
                return True
        return False

    def revert(self, buffer) -> bool:
        if self.last_expanded is None:
            return False
        document = buffer.document
        expansion = self.last_expanded.expanded + " "
        if not document.text_before_cursor.endswith(expansion):
            return False
        buffer.delete_before_cursor(count=len(expansion))
        buffer.insert_text(self.last_expanded.word)
        self.last_expanded = None
        return True


EDIT_SYMBOL = "<edit>"


def get_abbreviated(key: str, buffer) -> str:
    abbr = abbrevs[key]
    if callable(abbr):
        text = abbr(buffer=buffer, word=key)
    else:
        text = abbr
    return text


def set_cursor_position(buffer, expanded: str) -> None:
    pos = expanded.rfind(EDIT_SYMBOL)
    if pos == -1:
        return
    buffer.cursor_position = buffer.cursor_position - (len(expanded) - pos)
    buffer.delete(len(EDIT_SYMBOL))


def custom_keybindings(bindings, **kw):
    from prompt_toolkit.filters import EmacsInsertMode, ViInsertMode
    from xonsh.ptk_shell.key_bindings import carriage_return

    handler = bindings.add
    insert_mode = ViInsertMode() | EmacsInsertMode()
    abbrev = Abbreviation()

    @handler(" ", filter=IsMultiline() & insert_mode)
    def handle_space(event):
        buffer = event.app.current_buffer

        add_space = True
        if not abbrev.revert(buffer):
            position_changed = abbrev.expand(buffer)
            if position_changed:
                add_space = False
        if add_space:
            buffer.insert_text(" ")

    @handler(
        Keys.ControlJ, filter=IsMultiline() & insert_mode & ~completion_is_selected
    )
    @handler(
        Keys.ControlM, filter=IsMultiline() & insert_mode & ~completion_is_selected
    )
    def multiline_carriage_return(event):
        buffer = event.app.current_buffer
        current_char = buffer.document.current_char
        if not current_char or current_char.isspace():
            abbrev.expand(buffer)
        carriage_return(buffer, event.cli)


def _load_xontrib_(xsh: XonshSession, **_):
    xsh.builtins.events.on_ptk_create(custom_keybindings)
    # XSH.builtins is a namespace and extendable
    xsh.builtins.abbrevs = abbrevs
    proxy = DynamicAccessProxy("abbrevs", "__xonsh__.builtins.abbrevs")
    builtins.abbrevs = proxy  # type: ignore

    return {"abbrevs": abbrevs}


# # TODO: Implement adding the abbrevs section into `xonfig web`.
#
# import sys
# import inspect
# from xonsh.webconfig.routes import Routes, XontribsPage
#
# class AbbrevsPage(Routes):
#     path = "/abbrevs"
#     mod_name = XontribsPage.mod_name("abbrevs")
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         # lazy import as to not load by accident
#         from xontrib.abbrevs import abbrevs  # type: ignore
#
#         self.abbrevs: "dict[str, str]" = abbrevs
#
#     @classmethod
#     def nav_title(cls):
#         if cls.mod_name in sys.modules:
#             return "Abbrevs"
#
#     def get_header(self):
#         yield t.tr()[
#             t.th("text-right")["Name"],
#             t.th()["Value"],
#         ]
#
#     def get_rows(self):
#         for name in sorted(self.abbrevs.keys()):
#             alias = self.abbrevs[name]
#             if callable(alias):
#                 display = inspect.getsource(alias)
#             else:
#                 display = str(alias)
#             # todo:
#             #  2. way to update
#
#             yield t.tr()[
#                 t.td("text-right")[str(name)],
#                 t.td()[
#                     t.p()[repr(display)],
#                 ],
#             ]
#
#     def get_table(self):
#         rows = list(self.get_rows())
#         yield t.tbl("table-sm", "table-striped")[
#             self.get_header(),
#             rows,
#         ]
#
#     def get(self):
#         yield t.div("table-responsive")[self.get_table()]
