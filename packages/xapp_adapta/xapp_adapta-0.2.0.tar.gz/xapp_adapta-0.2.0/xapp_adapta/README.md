# A python module using libadapta

A project kind of with libadwaita, but using libadapta and XApp if possible.
It also makes a handy template for building python modules including `C++`
source. This is handy as it keeps desktop theming in Linux Mint `Zara` (22.2).
It might be expanded later.

## Notes for Developers

This is the `PyPI` readme. Included commands can be used for effect. Add
any commands to the `pyproject.toml` in the source linked below.

### Changing the Application ID

Are you sure you've changed any `xapp_adapta` references to be unique?
Please check `pyproject.toml` and also rename the module directory from
`xapp_adapta`. Also check that `_` is not `-`. Quite a bit auto fills the
about dialog, and the `[tool.metadata]` section is for a domain base
for the unique naming of resources, so includes a domain name.

## Commands in this Repository

Included commands (add more):

- `adapta_test` the basic original python demo of `libadapta`. Added a try catch
  to make `àdwaita` be used instead if `àdapta` is not present. Plus more.
- `adapta_main` extends the test `MainWindow` class for effect.
- `adapta_make_local` to install `.desktop`, `.svg` and locale `.mo` files.
  The `~/.local/share/applications/*.desktop` files might need edits.
- `adapta_remove_local` is an uninstall to clean the user's `~/.local/share` of
  just the installed files which `adapta_make_local` placed.
- ...

Thanks

_Simon Jackson_

## Links

[Template Source](https://github.com/jackokring/mint-python-adapta)
