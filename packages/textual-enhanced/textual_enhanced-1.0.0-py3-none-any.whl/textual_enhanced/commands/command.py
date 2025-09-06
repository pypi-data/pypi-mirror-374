"""Provides the base class for all application command messages."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from re import Pattern, compile
from typing import Final

##############################################################################
# Textual imports.
from textual.binding import Binding, BindingType
from textual.message import Message


##############################################################################
class Command(Message):
    """Base class for all application command messages."""

    COMMAND: str | None = None
    """The text for the command.

    Notes:
        If no `COMMAND` is provided the class name will be used.
    """

    ACTION: str | None = None
    """The action to call when the command is executed.

    By default the action will be:

       `action_{snake-case-of-command}_command`

    There are some commands that will result in unhelpful snake-case names,
    and also times where you want the action method named in a better way;
    in such cases use `ACTION` to override the method name.
    """

    FOOTER_TEXT: str | None = None
    """The text to show in the footer.

    Notes:
        If no `FOOTER_TEXT` is provided the
        [`command`][textual_enhanced.commands.Command.command] will be used.
    """

    SHOW_IN_FOOTER: bool = False
    """Should the command be shown in the [footer][textual.widgets.Footer]?

    By default commands are *not* shown in the
    [footer][textual.widgets.Footer], so set this to [`True`][True] to have
    the command appear there.
    """

    BINDING_KEY: str | tuple[str, str] | None = None
    """The binding key for the command.

    This can either be a string, which is the keys to bind, a tuple of the
    keys and also an overriding display value, or [`None`][None].
    """

    _SPLITTER: Final[Pattern[str]] = compile("[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)")
    """Regular expression for splitting up a command name."""

    @classmethod
    def command(cls) -> str:
        """The text for the command.

        Returns:
            The command's textual name.
        """
        return cls.COMMAND or " ".join(cls._SPLITTER.findall(cls.__name__))

    @property
    def context_command(self) -> str:
        """The command in context."""
        return self.command()

    @classmethod
    def tooltip(cls) -> str:
        """The tooltip for the command."""
        return cls.__doc__ or ""

    @property
    def context_tooltip(self) -> str:
        """The tooltip for the command, in context."""
        return self.tooltip()

    @classmethod
    def key_binding(cls) -> str:
        """Get the key that is the binding for this command.

        Returns:
            The key that is bound, or [`None`][None] if there isn't one.

        Notes:
            If a command has multiple bindings, only the first key is
            returned.
        """
        if isinstance(key := cls.BINDING_KEY, tuple):
            key, *_ = key
        if isinstance(key, str):
            key, *_ = cls.binding().key.partition(",")
        return (key or "").strip()

    @classmethod
    def action_name(cls) -> str:
        """Get the action name for the command.

        Returns:
            The action name.
        """
        return (
            cls.ACTION
            or f"{'_'.join(cls._SPLITTER.findall(cls.__name__))}_command".lower()
        )

    @staticmethod
    def bindings(*bindings: BindingType | type[Command]) -> list[BindingType]:
        """Create bindings.

        Args:
            bindings: Normal Textual bindings or a command class.

        Returns:
            A list of bindings that can be used with [`BINDINGS`][textual.dom.DOMNode.BINDINGS].
        """
        return [
            (binding if isinstance(binding, (Binding, tuple)) else binding.binding())
            for binding in bindings
        ]

    @classmethod
    def binding(cls) -> Binding:
        """Create a binding object for the command.

        Returns:
            A [`Binding`][textual.binding.Binding] for the command's key bindings.

        Raises:
            ValueError: If the command has no key binding.
        """
        if not cls.BINDING_KEY:
            raise ValueError("No binding key defined, unable to create a binding")
        keys, display = (
            cls.BINDING_KEY
            if isinstance(cls.BINDING_KEY, tuple)
            else (cls.BINDING_KEY, None)
        )
        return Binding(
            keys,
            cls.action_name(),
            description=cls.FOOTER_TEXT or cls.command(),
            tooltip=cls.tooltip(),
            show=cls.SHOW_IN_FOOTER,
            key_display=display,
            id=cls.__name__,
        )

    @property
    def has_binding(self) -> bool:
        """Does this command have a binding?"""
        return self.BINDING_KEY is not None


### command.py ends here
