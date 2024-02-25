from pathlib import Path

from click.testing import CliRunner

from extmake.cli import main


def test_basic_include(test_makefile, capfd, clear_cache):
    runner = CliRunner()
    result = runner.invoke(main, ["-f", test_makefile, "all"])
    assert result.exit_code == 0
    assert capfd.readouterr().out == "this is included\n"


def test_nested_include(test_makefile, capfd, clear_cache):
    # change the included file to create nesting:
    mkfile_content = test_makefile.read_text()
    mkfile_content.replace("include.mk", "nesting_include.mk")
    test_makefile.write_text(mkfile_content)
    # run the test:
    runner = CliRunner()
    result = runner.invoke(main, ["-f", test_makefile, "all"])
    assert result.exit_code == 0
    assert capfd.readouterr().out == "this is included\n"


def test_successive_calls(test_makefile, capfd, clear_cache):
    # this test ensures that the caching logic is not breaking anything
    runner = CliRunner()
    for _ in range(2):
        result = runner.invoke(main, ["-f", test_makefile, "all"])
        assert result.exit_code == 0
        assert capfd.readouterr().out == "this is included\n"


def test_error_no_makefile(test_makefile, clear_cache):
    runner = CliRunner()
    result = runner.invoke(main, ["-f", "does_not_exist"])
    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_error_proxied_from_make(test_makefile, capfd, clear_cache):
    runner = CliRunner()
    result = runner.invoke(main, ["-f", test_makefile, "unknown_target"])
    assert result.exit_code == 2
    assert "no rule to make target" in capfd.readouterr().err.lower()


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "You are using ExtMake" in result.output


def test_verbose(test_makefile, local_repo, caplog, clear_cache):
    caplog.set_level("DEBUG")
    runner = CliRunner()
    result = runner.invoke(main, ["--verbose", "-f", test_makefile, "all"])
    assert f"No cache found for {test_makefile}, preprocessing" in caplog.text
    assert f"Cloning {local_repo.as_uri()}" in caplog.text
