# tw-cli

> Run scratch projects in the terminal

- Uses playwright and turbowarp scaffolding
- Supports the turbowarp debugger's log, warn, error and breakpoint blocks.
- Supports exit codes with the `TW-CLI: exit code` variable **for all sprites**.

## Installation

`pip install turbowarp-cli`

<details>
<summary>Bleeding edge:</summary>
1. git clone this repo
2. `pip install -e .`
3. to update, use `git pull`
</details>

## Usage

`twcli run <Project path>`

It only works on project files.

---

If you want to automatically supply inputs to `ask and wait` blocks, use the -i command:

`twcli run .\Project.sb3 -i "hi" "there`

This provides the arguments:
- `hi`
- `there`

If you want to disable headless mode (to see the browser), use `-H`:

`twcli run .\Project.sb3 -i "hi" "there" -H`
