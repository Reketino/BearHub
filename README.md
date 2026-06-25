# BearHub 🐻

> Did you feel emptiness when finally switching to Linux and leaving Logitech G Hub behind?
>
> Did you discover that all your carefully crafted macros were trapped inside a mysterious `settings.db` file?
>
> Did you search the internet only to find outdated forum posts and broken scripts?
>
> Well... I got your back, pal.

## What is BearHub?

BearHub is an open-source tool for importing Logitech G Hub macros from Windows and making them usable outside of G Hub.

Currently, BearHub can:

* Import Logitech G Hub `settings.db`
* Extract text macros
* Extract macro bindings
* Detect assigned G-keys
* Export everything into a clean JSON profile format
* Browse imported macros in a simple GUI

Example:

```text
G1 -> {}
G2 -> []
G3 -> ()
G4 -> <>
G5 -> =>
```

## Why?

I switched to Linux and quickly discovered that all my coding macros were still living inside Logitech G Hub on Windows.

There was no easy way to extract them, manage them, or migrate them.

So BearHub was born.

## The Great settings.db Scavenger Hunt

Logitech does not provide a convenient "Export Macros" button.

Instead, your macros live inside a SQLite database called:

settings.db

Unfortunately, the exact location can vary between G Hub versions and installations.

Common places to look:

C:\Users\<username>\AppData\Local\LGHUB\
C:\Users\<username>\AppData\Roaming\LGHUB\
C:\ProgramData\LGHUB\

If all else fails:

Search your entire drive for:

settings.db

That's exactly how BearHub was born.

## Current Status

✔ Import G Hub database

✔ Parse Logitech profiles

✔ Extract text macros

✔ Extract key bindings

✔ Export BearHub profiles

🚧 Linux macro execution

🚧 Profile editor

🚧 Import/export between computers

🚧 Automatic keyboard integration

## Roadmap

### Phase 1

* Import macros from Logitech G Hub
* Build BearHub profile format
* Create profile browser

### Phase 2

* Edit macros inside BearHub
* Create new macros
* Export profiles

### Phase 3

* Native Linux macro engine
* Bind macros directly to keyboard shortcuts
* Run BearHub without Logitech software

### Phase 4

* Support additional devices
* Razer Synapse import
* Community profiles

## Disclaimer

BearHub is not affiliated with Logitech.

This project was created because I wanted my macros back.
