# status-bar-pass
A MacOs Status Bar utility for accessing your `.gpg` encrypted secrets (generated via something like [linux pass](https://formulae.brew.sh/formula/pass))

## Installation
Download the latest release `.zip` file from the [releases page](https://github.com/geoff-va/status-bar-pass/releases), unzip it and double click the `.app` file. It may indicate the app is from an untrusted developer and not allow you to run it. You can right click and select `open` and choose to run it anyway or you're welcome to build it from source yourself.

## Prerequisites
This project uses `python-gngpg` which requires a `gpg` binary to be installed. You will need the path of this binary which can be found by running `which gpg` from a terminal shell.

## Options and Setup
The first time you run the application the following default options are used:
- Password Store Directory: `~/.password-store`
    - Root directory passwords (`.gpg` files) will be fetched from.
- GPG Home: `~/.gnupg`
    - Home directory for `gpg` usage. Can be found via `gpg --version | grep Home`.
- GPG Binary Path: likely unset by default
    - Path to the `gpg` binary used by `python-gnupg`

These can be changed at any time in the options menu. If the `gpg` binary path is not set it will ask you for it the first time you try to decrypt a password.

## Usage
Select the password you want to decrypt from the menu then click `Copy` or `Show`!

The most recently accessed passwords are shown in the `Recents` menu.

The `gpg` agent is used, so if you've recently entered your decryption password you can click `Copy` or `Show` without entering anything and if it's still cached, it will succeed. Otherwise it will ask you to enter the password again.

## Build and Development
- Clone the repo
- Create a Framework Based virtual environment (Like one from python.org - currently built with Python 3.10.8)
- `pip install -r requirements/dev.txt`
- Build with Alias: `python build_app.py py2app -A`
    - Run: `./dist/SbPass.app/Contents/MacOS/SbPass`
- Build as standalone Release: `python build_app.py py2app`
    - `.app` file will be in `./dist`
- Run tests: `pytest ./tests`
