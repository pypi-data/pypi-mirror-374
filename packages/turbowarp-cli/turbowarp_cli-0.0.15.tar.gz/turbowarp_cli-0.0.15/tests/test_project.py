def test_project():
    from pathlib import Path

    from twcli.run import run, get_exit_code

    __file_path__ = Path(__file__).resolve()

    proj_path = (__file_path__ / '..' / '..' / "Project.sb3").resolve()

    assert proj_path.exists()

    assert get_exit_code(run(proj_path.read_bytes(), """\
faretek
yes
no""")) == "0.5"
