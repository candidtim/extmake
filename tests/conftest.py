import shutil
import subprocess

import pytest

from extmake import cache


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
