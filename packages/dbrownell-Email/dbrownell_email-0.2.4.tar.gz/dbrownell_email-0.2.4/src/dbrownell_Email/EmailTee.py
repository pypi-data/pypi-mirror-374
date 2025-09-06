"""Run a process and tee its output to an email message and the console."""

from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Annotated

import typer

from ansi2html.converter import Ansi2HTMLConverter
from typer.core import TyperGroup

from dbrownell_Common.Streams.Capabilities import Capabilities
from dbrownell_Common.Streams.DoneManager import DoneManager, Flags as DoneManagerFlags
from dbrownell_Common.Streams.StreamDecorator import StreamDecorator
from dbrownell_Common import SubprocessEx
from dbrownell_Email.SmtpMailer import SmtpMailer


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):  # noqa: D101
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs) -> list[str]:  # noqa: ARG002, D102
        return list(self.commands.keys())


# ----------------------------------------------------------------------
app = typer.Typer(
    cls=NaturalOrderGrouper,
    help=__doc__,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)


# ----------------------------------------------------------------------
@app.command(
    "EntryPoint",
    help=__doc__,
    no_args_is_help=True,
)
def EntryPoint(  # noqa: D103
    command_line: Annotated[
        str,
        typer.Argument(
            ...,
            help="Command line to invoke; all output will be included in the email message. If the argument begins with '@', the rest of the command line will be interpreted as a filename and the command line will be read from that file.",
        ),
    ],
    smtp_profile_name: Annotated[
        str,
        typer.Argument(..., help="SMTP profile name."),
    ],
    email_recipients: Annotated[
        list[str],
        typer.Argument(..., help="Recipient(s) for the email message."),
    ],
    email_subject: Annotated[
        str,
        typer.Argument(
            ...,
            help="Subject of the email message; '{now}' can be used in the string as a template placeholder for the current time.",
        ),
    ],
    output_filename: Annotated[
        Path | None,
        typer.Option(
            "--output-filename",
            dir_okay=False,
            resolve_path=True,
            help="Writes formatted html output to a file; this is useful when --force-color has also been specified as an argument.",
        ),
    ] = None,
    background_color: Annotated[
        str,
        typer.Option("--background-color", help="Email background color."),
    ] = "black",
    verbose: Annotated[  # noqa: FBT002
        bool,
        typer.Option("--verbose", help="Write verbose information to the terminal."),
    ] = False,
    debug: Annotated[  # noqa: FBT002
        bool,
        typer.Option("--debug", help="Write debug information to the terminal."),
    ] = False,
) -> None:
    with DoneManager.CreateCommandLine(
        flags=DoneManagerFlags.Create(verbose=verbose, debug=debug),
    ) as dm:
        try:
            smtp_mailer = SmtpMailer.Load(smtp_profile_name)
        except Exception as ex:
            dm.WriteError(str(ex))
            return

        with dm.Nested(
            "Running command...",
            suffix="\n",
        ) as running_dm:
            # Create the stream used to capture the message content
            message_sink = StringIO()

            Capabilities.Set(
                message_sink,
                Capabilities(
                    is_interactive=False,
                    supports_colors=True,
                    is_headless=True,
                ),
                no_column_warning=True,
            )

            with running_dm.YieldStream() as dm_stream:
                running_dm.result = SubprocessEx.Stream(
                    command_line,
                    StreamDecorator([message_sink, dm_stream]),
                )

            message = message_sink.getvalue()

        with dm.Nested(
            "Processing output...",
            suffix="\n",
        ) as processing_dm:
            title = None

            if output_filename:
                title = output_filename.stem

            # Value to convert spaces into before the text is converted to html.
            space_placeholder = "__nbsp;__"

            with processing_dm.Nested("Converting output to HTML..."):
                message = message.replace(" ", space_placeholder)

                message = Ansi2HTMLConverter(
                    dark_bg=True,
                    inline=True,
                    line_wrap=False,
                    title=title or "",
                ).convert(message)

            for source, dest in [
                (space_placeholder, "&nbsp;"),
                # Create a div to set the background color
                (
                    '<pre class="ansi2html-content">\n',
                    '<pre class="ansi2html-content">\n<div style="background-color: {}">\n'.format(
                        background_color
                    ),
                ),
                # Undo the div that set the background color
                (
                    "</pre>\n",
                    "</div>\n</pre>\n",
                ),
            ]:
                message = message.replace(source, dest)

            if output_filename is not None:
                with processing_dm.Nested("Writing to '{}'...".format(output_filename)):
                    output_filename.parent.mkdir(parents=True, exist_ok=True)

                    with output_filename.open("w", encoding="utf-8") as f:
                        f.write(message)

        with dm.Nested("Sending email...") as email_dm:
            try:
                smtp_mailer.SendMessage(
                    email_recipients,
                    email_subject.format(now=datetime.now()),  # noqa: DTZ005
                    message,
                    message_format="html",
                )
            except Exception as ex:
                email_dm.WriteError(str(ex))
                return


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
