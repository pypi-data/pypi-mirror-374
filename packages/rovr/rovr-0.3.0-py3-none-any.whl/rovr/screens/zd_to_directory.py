from subprocess import run

from textual import events, work
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.content import Content
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

from rovr.functions import path as path_utils


class ZDToDirectory(ModalScreen):
    """Screen with a dialog to z to a directory, using zoxide"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._queued_task = None
        self._queued_task_args: str | None = None

    def compose(self) -> ComposeResult:
        with VerticalGroup(id="zoxide_group", classes="zoxide_group"):
            yield Input(
                id="zoxide_input",
                placeholder="Enter directory name or pattern",
            )
            yield OptionList(
                Option("  No input provided", disabled=True),
                id="zoxide_options",
                classes="empty",
            )

    def on_mount(self) -> None:
        zoxide_input = self.query_one("#zoxide_input")
        zoxide_input.border_title = "zoxide"
        zoxide_input.focus()
        zoxide_options = self.query_one("#zoxide_options")
        zoxide_options.border_title = "Folders"
        zoxide_options.can_focus = False
        self.zoxide_updater(Input.Changed(zoxide_input, value=""))

    def on_input_changed(self, event: Input.Changed) -> None:
        if any(
            worker.is_running and worker.node is self for worker in self.app.workers
        ):
            self._queued_task = self.zoxide_updater
            self._queued_task_args = event
        else:
            self.zoxide_updater(event=event)

    def any_in_queue(self) -> bool:
        if self._queued_task is not None:
            self._queued_task(self._queued_task_args)
            self._queued_task, self._queued_task_args = None, None
            return True
        return False

    @work(thread=True)
    def zoxide_updater(self, event: Input.Changed) -> None:
        """Update the list"""
        search_term = self.query_one("#zoxide_input").value.strip()
        # check 1 for queue, to ignore subprocess as a whole
        if self.any_in_queue():
            return
        zoxide_output = run(
            ["zoxide", "query", "--list"] + search_term.split(),
            capture_output=True,
            text=True,
        )
        # check 2 for queue, to ignore mounting as a whole
        if self.any_in_queue():
            return
        zoxide_options = self.query_one("#zoxide_options", OptionList)
        zoxide_options.add_class("empty")
        options = []
        if zoxide_output.stdout:
            for line in zoxide_output.stdout.splitlines():
                options.append(
                    Option(Content(f" {line}"), id=path_utils.compress(line))
                )
            if len(options) == len(zoxide_options.options) and all(
                options[i].id == zoxide_options.options[i].id
                for i in range(len(options))
            ):  # ie same~ish query, resulting in same result
                pass
            else:
                # unline normally, I'm using an add_option**s** function
                # using it without has a likelihood of DuplicateID being
                # raised, or just nothing showing up. By having the clear
                # options and add options functions nearby, it hopefully
                # reduces the likelihood of an empty option list
                self.app.call_from_thread(zoxide_options.clear_options)
                self.app.call_from_thread(zoxide_options.add_options, options)
                zoxide_options.remove_class("empty")
                zoxide_options.highlighted = 0
        else:
            # No Matches to the query text
            self.app.call_from_thread(zoxide_options.clear_options)
            self.app.call_from_thread(
                zoxide_options.add_option,
                Option("  --No matches found--", disabled=True),
            )
        # check 3, if somehow there's a new request after the mount
        if self.any_in_queue():
            return  # nothing much to do now
        else:
            self._queued_task = None

    def on_input_submitted(self, event: Input.Submitted) -> None:
        zoxide_options = self.query_one("#zoxide_options")
        if zoxide_options.highlighted is None:
            zoxide_options.highlighted = 0
        zoxide_options.action_select()

    # You cant manually tab into the option list, but you can click, so I guess
    @work(exclusive=True)
    async def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        """Handle option selection."""
        selected_value = event.option.id
        assert selected_value is not None
        run(
            ["zoxide", "add", path_utils.decompress(selected_value)],
            capture_output=True,
            text=True,
        )
        if selected_value:
            self.dismiss(selected_value)
        else:
            self.dismiss(None)

    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        match event.key:
            case "escape":
                event.stop()
                self.dismiss(None)
            case "down":
                event.stop()
                zoxide_options = self.query_one("#zoxide_options")
                if zoxide_options.options:
                    zoxide_options.action_cursor_down()
            case "up":
                event.stop()
                zoxide_options = self.query_one("#zoxide_options")
                if zoxide_options.options:
                    zoxide_options.action_cursor_up()
            case "tab":
                event.stop()
                self.focus_next()
            case "shift+tab":
                event.stop()
                self.focus_previous()
