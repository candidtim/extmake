from pathlib import Path

from click.testing import CliRunner

from extmake import cache, cli


def test_print(test_makefile, clear_cache):
    runner = CliRunner()
    result = runner.invoke(cli.edit, ["print", "-f", test_makefile])
    assert result.exit_code == 0
    assert "@echo 'this is included'" in result.output


def test_eject(test_makefile, clear_cache):
    runner = CliRunner()
    result = runner.invoke(cli.edit, ["eject", "-f", test_makefile, "--yes"])
    assert result.exit_code == 0
    assert "@echo 'this is included'" in test_makefile.read_text()


def test_update(local_repo, test_makefile, caplog, clear_cache):
    caplog.set_level("DEBUG")
    runner = CliRunner()
    result = runner.invoke(cli.edit, ["update", "-f", test_makefile])
    assert result.exit_code == 0
    assert f"Pulling {local_repo.as_uri()}" in caplog.text


def test_cache_show():
    runner = CliRunner()
    result = runner.invoke(cli.edit, ["cache", "show"])
    assert result.exit_code == 0
    assert Path(result.output.strip()).is_dir()


def test_cache_clear_all(test_makefile, clear_cache):
    runner = CliRunner()
    result = runner.invoke(cli.edit, ["print", "-f", test_makefile])
    assert len(list(cache.cache_root().iterdir())) > 0
    result = runner.invoke(cli.edit, ["cache", "clear", "--all", "--yes"])
    assert result.exit_code == 0
    assert len(list(cache.cache_root().iterdir())) == 0


def test_cache_clear_for_file(test_makefile, clear_cache):
    runner = CliRunner()
    result = runner.invoke(cli.edit, ["print", "-f", test_makefile])
    assert len(list(cache.cache_root().iterdir())) > 0
    result = runner.invoke(cli.edit, ["cache", "clear", "-f", test_makefile, "--yes"])
    assert result.exit_code == 0
    assert len(list(cache.cache_root().iterdir())) == 0
