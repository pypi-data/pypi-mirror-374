# opengine2

A text box that allows easier input of many characters in a structured way.

Start typing in the text box.
Alternatives for each character typed is accessed in series
by repeatedly typing the same character,
like in an __o__ld __p__hone (hence the name).
As you type, gain feedback with which character you just typed in the display.
Finish by pressing "Quit & Copy",
which copies the text box's contents to the clipboard.

# Defining your own keyboards
By default an IPA keyboard is complete
and a partial Cyrillic and Greek keyboard is also provided
for proof of concept of keyboard switching.

To write your own keyboard,
put them in your XDG data path.
TOML and HOCON are supported.
The filename should end in `.opengine2.toml` or `.opengine2.hocon`
as needed.

Only three keys are needed in either case:

- `opengine2_version` defines the file as an opengine2-readable file
  and sets the version.
  This is always 1 for now.
- `name` gives the name as displayed in the GUI.
- `keys` is a list of two- or three-element lists.
  The first key

TOML is useful for machine generation.
If you handwrite your own keyboards,
HOCON is better because you don't need to type so many quotes.

The location for storing the files is still in flux
and may change as future versions require.

# Configuration file
Not yet implemented,
but the following keys are expected:

- `additional_files`: locations of additional keyboard files.
- `default_file`: name of default file.

It is placed in the usual location,
i.e. `~/.config/opengine2` or wherever your XDG environment variables are set.

# Possibly Asked Questions
## Why not an IME? ##
Mostly because I can't quite figure out how to make it (`ibus`) work,
but also because this is fairly unusual behaviour for an IME.
Generally an IME would not demand repeated entry of a key to switch alternatives.

## Why version 2? ##
Version 1 was an AutoHotkey script.
It's well over 10 years old now but it is still usable.
However, AHK is poorly supported on Linux
so I had to make something else to replace it.
