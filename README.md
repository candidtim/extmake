# ExtMake - `make` wrapper with `include git=...` and more

ExtMake is a loose wordplay on a "**make** with an ability to include
**ext**ernal Makefiles".

While `make` supports the `include` directive, it can only include files from a
local file system. ExtMake adds an ability to include files from Git
repositories and stays out of the way for everything else. You can see ExtMake
as a preprocessor or a wrapper around `make`.

Features:

 - backward-comptible syntax: any valid `Makefile` is valid for `extmake`
 - no new syntax except for the added support of `git=...` extension for the
   `include` directive
 - straightforward implementation reuses `make` for everything else
 - forward-compatible: ability to eject the configuration into a single
   self-contained `Makefile`

## Motivation

Makefiles are often (ab?)used for task automation in the projects not related
to C. But they are hardly reusable and often get copy-pasted between projects.
Tools for project templating - for example, Cookicutter or Copier in the Python
ecosystem - may be used to facilitate this, but have their drawbacks. Instead,
why not apply the same approach as in all other code - declare a dependency and
load a reusable implementation from a "library"? This is the problem ExtMake is
set to solve, with a touch of simplicity and minimalism.

## Example

File `Makefile` in a GitHub repository "example/test":

    test:
        poetry run pytest --cov-report term --cov=myproj tests/

File `Makefile`:

    include git=git@github.com:example/test.git;rev=1.0.0

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
 - Git

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

The `include` directive is supported by `make` natively and interprets the
arguments as file paths. On top of that, ExtMake can interpret the argument as
a reference to a Git repository. For simplicity, a single Git reference is
allowed for each `include` directive.

    include git=URL[;key=value]...

The argument is a [DSN](https://en.wikipedia.org/wiki/Data_source_name)
formatted as a series of `key=value` pairs separated by a semicolon `;`.
Following keys are supported:

 - `git`: a Git repository URL, such that can be used with `git clone`; this
   is the only mandatory key
 - `rev`: a Git commit reference, such as a branch name, a tag name, or a SHA;
   defaults to `master`
 - `path`: a path within a repository pointing to the file to be included;
   defaults to `Makefile`

As with the original `include` directive, included resources are inserted
verbatim at the location of the directive. Issues such as conflicting target
names, for example, are not controlled and `make` is left to do its job and
report any further syntax warning or errors.

Presently, nested Git includes are not supported: included files are not
preprocessed.

### Best practices

 - To keep the builds reproducible, it is best to set the `rev` to a tag
     - If you don't use tags for the `rev`, you can run `extmake-edit cache
       clear` to force the update of the dependencies
 - `*.mk` is a common naming convention for the files that are to be included

### Using public or private Git servers

ExtMake uses Git to clone the repository and will effectively reuse the SSH
config to authenticate with a private server, for example.

For example, in a file `~/.ssh/config`:

    Host gitlab.example.com
        HostName gitlab.example.com
        User git
        IdentityFile ~/.ssh/my_rsa

### Eject

At any time you can stop using ExtMake. Ejecting will resolve all includes and
generate a single complete Makefile with all included content embedded into it:

    extmake-edit eject [--file FILE]

## Troubleshooting

 - For better performance, both the dependencies and the resolved `Makefiles`
   are cached in the user data directory (somewhere in user `$HOME`, depending
   on the OS). In case of problems, try clearing the cache with `extmake-edit
   cache clear`.

 - Feel free to [report a bug](https://github.com/candidtim/extmake/issues).

## Future features

 - A command to list all dependencies
 - A hint about the use of ExtMake in case of errors raised by `make`.
 - Better error handling: when `make` or `git` are not available, all internal
   errors.
 - PyPI distribution.
 - Resolve included target names, allow overrides.
   - Add the `#super make TARGET` directive (or interpret `make super.TARGET`?)
   - A command to generate an override, like `extmake-edit override TARGET`.
 - Allow overriding the variables defined in the included files with `?=`.
 - Update policy to control how often the cloned repositories are updated.
   E.g., `update=manual|always` in the DSN.
