import base64
import warnings

from pathlib import Path
from typing import TypedDict, Literal, Optional

from rich.console import Console

# noinspection PyProtectedMember
from playwright.sync_api import sync_playwright

CONSOLE = Console(force_terminal=True)

class LogMessage(TypedDict):
    type: Literal['log', 'warn', 'error', 'breakpoint', 'exit_code', 'say', 'think']
    content: Optional[str]


__file_path__ = Path(__file__).resolve()
run_html_path = (__file_path__ / '..' / "run.html").resolve()
tw_scaffolding_path = (__file_path__ / '..' / "scaffolding-with-music.js").resolve()

def get_exit_code(output: list[LogMessage], default: Optional[str]=None) -> Optional[str]:
    ret = output[-1]
    return ret["content"] if ret["type"] == "exit_code" else default

def output_msg(msg: LogMessage):
    """
    Print a log message to console with colored formatting. Automatically used by run()
    :param msg: Log message dictionary
    """
    cat = msg['type']
    content = msg.get('content')

    # noinspection PyUnreachableCode
    match cat:
        case 'log':
            CONSOLE.print(f"Log: {content!r}", style="green")
        case 'warn':
            CONSOLE.print(f"Warn: {content!r}", style="yellow")
        case 'error':
            CONSOLE.print(f"Error: {content!r}", style="red")
        case 'breakpoint':
            CONSOLE.print(f"Breakpoint", style="red")
        case 'exit_code':
            CONSOLE.print(f"Exited with code {content!r}", style="default")
        case 'say':
            CONSOLE.print(f"Say: {content!r}", style="purple")
        case 'think':
            CONSOLE.print(f"Think: {content!r}", style="purple")
        case _:
            warnings.warn(f"Unknown message: {msg!r}")
            CONSOLE.print(f"{msg['type']}: {msg.get('content', '')!r}")


def run(sb3_file: bytes,
        input_args_str: Optional[str] = None,
        *,
        headless: bool = True) -> list[LogMessage]:
    """
    Run a scratch project.
    :param sb3_file: Scratch project to run, in bytes
    :param input_args_str: arguments that are passed to any 'ask' ui, split by newlines. If these run out, then you will be prompted
    :param headless: Whether to run playwright in headless mode (whether to hide the window)
    :return: List of log messages from scratch project
    """
    input_args: list[str]
    if input_args_str is None:
        input_args = []
    else:
        input_args = input_args_str.split('\n')

    def get_arg():
        get_output()
        if input_args:
            arg = input_args.pop(0)
            CONSOLE.print(f">> {arg!r}")
            return arg
        else:
            return input(">> ")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page()

        assert run_html_path.exists()
        assert tw_scaffolding_path.exists()

        page.goto(f"file://{run_html_path}"
                  f"?project={base64.urlsafe_b64encode(sb3_file).decode()}")

        while True:
            if not page.query_selector("#project"):
                warnings.warn("#project not found")
            else:
                break

        running = True

        def dialogmanage(dialog):
            # when a dialog pops up, we just exit. assume its the end of the program
            nonlocal running
            dialog.accept()
            running = False

        page.on("dialog", dialogmanage)

        output_i = 0  # index of next message

        def get_output() -> list[LogMessage]:
            """
            Handle and return output. If new messages are received, print them.
            """
            nonlocal output_i
            try:
                output = page.evaluate("output")
            except Exception as e:
                warnings.warn(f"Caught exception: {e}")
                output = []

            while len(output) > output_i:
                output_msg(output[output_i])
                output_i += 1

            return output

        while running:
            get_output()

            sc_input = page.query_selector(".sc-question-input")
            if sc_input is not None:
                sc_input.type(get_arg() + '\n')

        return get_output()
