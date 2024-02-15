# ExtMake - `make` wrapper with #include and more

ExtMake is a loose wordplay on a "**make** with an ability to include
**ext**ernal Makefiles".

Makefiles are often (ab?)used for task automation in the projects not related
to C. But they are hardly reusable and often get copy-pasted between projects.
Tools for project templating - for example, Cookicutter or Copier in the Python
ecosystem - may be used to facilitate this, but have their drawbacks. Instead,
why not apply the same approach as in all other code - declare a dependency and
load a reusable implementation from a "library"? This is the problem ExtMake is
set to solve, with a touch of simplicity and minimalism.

`extmake` is a simple **wrapper** over `make` with the following features:

 - no new syntax (not outside comments), uses regular Makefiles
 - the `#include` directive
 - include from both local files and remote repositories, private or public
 - straightforward implementation reuses `make` for everything else
 - ability to eject the configuration into a single self-contained Makefile

## Example

File `Makefile` in a GitHub repository "example/common":

    test:
        poetry run pytest --cov-report term --cov=myproj tests/

File `Makefile`:

    #include "example/common@master"

    build: test
        poetry build

Usage:

    extmake build

## Status

In active development, unstable.

## Installation

The tool is currently not stable enough to be published. Clone this repository
if you are interested in using it in the meantime.

If you prefer so, you can safely alias `extmake` to `make`. ExtMake will
process regular Makefiles by simply proxying them to `make`, albeit with some
overhead.

## Dependencies

 - Make
 - Git, if you include files from GitHub or other Git servers

## Usage

### extmake

`extmake` is a wrapper over `make` and proxies all inputs and outputs almost
unchanged. As such, usage in the command line is exactly the same as with a
regular `make`.

To avoid ambiguity, `extmake` may remind the user that they use the `extmake`
wrapper in case of errors, for example. A dedicated message is added to the
stdout in this case, keeping the rest of the original `make` output intact.

### extmake-edit

To keep the `extmake` usage transparent with regard to `make`, all commands
specific to ExtMake are available through `extmake-edit`.

`extmake-edit` may be used to debug the Makefile resolution, or eject from
ExtMake, altogether.

For usage, run:

    extmake-edit --help

### Syntax

In the current implementation, ExtMake adds a single directive: `#include`:

    #include "PATH"

where `PATH` can be one of:

 - Local file path, pointing to any file (not necessarily a `Makfile`)
 - A string in the format `vendor/repository@ref`. By default, it is assumed to
   be a GitHub reference (`username/repository`), but this can be overriden in
   the ExtMake configuration to point to another public or private repository.
   The repository is expected to have a `Makefile` in its root. `ref` is a Git
   commit reference, such as branch name, tag name or a commit SHA.

In the current implementation, syntax parsing is quite naive: included
resources are inserted verbatim at the location of the `#include` directive.
Issues such as conflicting target names, for example, are not controlled, while
`make` is left to do its job and report any further syntax errors and warnings.

Presently, nested includes are not supported: included files are not
preprocessed.

### Eject

At any time you can stop using ExtMake. Ejecting will resolve all includes and
generate a single complete Makefile with all included content embedded into it:

    extmake-edit eject [--file FILE]

## Configuration

ExtMake looks up for the configuration files in the user config dirs, depending
on the host OS:

 - Linux: `~/.config/extmake/config.toml`
 - MacOS: TBD
 - Windows: TBD

### Using public or private Git servers

By default, ExtMake assumes that `"vendor/repository"` in the include
directives corresponds to GitHub `"username/repository"`. Configuration allows
defining a different Git server associated with a `"verndor"` key:

    [extmake.respositories]
    somevendor = gitlab.example.com

ExtMake uses Git to clone the repository and will effectively reuse the SSH
config to authenticate with a private server, for example.

For example, in a file `~/.ssh/config`:

    Host gitlab.example.com
        HostName gitlab.example.com
        User git
        IdentityFile ~/.ssh/my_rsa

## Troubleshooting

In case of problems, try clearing the cache:

    extmake-edit cache clear

Feel free to [report a bug](https://github.com/candidtim/extmake/issues).

## Internals

`extmake` resolves all `#include` directives by finding the declared
"dependencies" and producing a new `Makefile` where all includes are
substituted by the content of the included files.

For better performance, both the dependencies and the resolved `Makefiles` are
cached in the user data directory (somewhere in user `$HOME`, depending on the
OS).

## Future features

 - Include from remote repositories: GitHub.
 - Include from remote repositories: support custom repositories through a
   configuration.
 - Include from remote repositories: custom paths with the remote repo.
 - A hint about the use of ExtMake in `make --help` and in case of errors
   raised by `make`.
 - Better error handling: when `make` or `git` are not available, all internal
   errors.
 - Parse the `--file` (`-f`, `--makefile`) argument and do not proxy it.
   - Same for the `eject` command.
 - Resolve included target names, allow overrides.
   - Add the `#super make TARGET` directive.
   - A command to generate an override, like `extmake-edit override TARGET`.
 - Nested includes.
 - Allow overriding the variables defined in the included files with `?=`.
 - Generate a sample configuration file (`config.toml.example`) alongside the
   config file, or propose another way to generate the configuration file.
 - A command to print user data (cache) and config locations.
 - PyPI distribution.
