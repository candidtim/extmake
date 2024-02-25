import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from extmake import cache
from extmake.cli import main


@pytest.fixture
def local_repo(tmp_path):
    repo = tmp_path / "repo"
    repo_url = repo.as_uri()
    repo.mkdir()
    include_file = repo / "include.mk"
    include_file.write_text("included:\n\t@echo 'this is included'\n")
    nesting_include_file = repo / "nesting_include.mk"
    nesting_include_file.write_text(f"include git={repo_url};path=include.mk\n")
    subprocess.run(["git", "init"], cwd=repo)
    subprocess.run(["git", "add", "."], cwd=repo)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo)
    yield repo
    shutil.rmtree(repo)


@pytest.fixture
def test_makefile(tmp_path, local_repo):
    local_repo_url = local_repo.as_uri()
    makefile = tmp_path / "Makefile"
    makefile.write_text(
        f"include git={local_repo_url};path=include.mk\n\nall: included\n"
    )
    yield makefile
    makefile.unlink()


@pytest.fixture
def clear_cache():
    yield
    cache.clear_all()


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
