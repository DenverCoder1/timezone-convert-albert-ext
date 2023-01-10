# timezone-convert-albert-ext

> **Warning**: This plugin is not supported in Albert >= 0.18

[![discord](https://custom-icon-badges.herokuapp.com/discord/819650821314052106?color=5865F2&logo=discord-outline&logoColor=white "Dev Pro Tips Discussion & Support Server")](https://discord.gg/fPrdqh3Zfu)
[![License MIT](https://custom-icon-badges.herokuapp.com/github/license/DenverCoder1/timezone-convert-albert-ext.svg?logo=repo)](https://github.com/DenverCoder1/timezone-convert-albert-ext/blob/main/LICENSE)
[![code style black](https://custom-icon-badges.herokuapp.com/badge/code%20style-black-black.svg?logo=black-b&logoColor=white)](https://github.com/psf/black)

Extension for converting between timezones in [Albert launcher](https://albertlauncher.github.io/)

![demo](https://user-images.githubusercontent.com/20955511/142350619-0b84305e-0422-4e0c-8ecc-d1f6cdac540a.gif)

## Installation

1. Locate the `modules` directory in the Python extension data directory.

The data directories reside in the data directories of the application defined by Qt. Hence on linux the modules would be looked up in the following directories (in this order):

```
~/.local/share/albert/org.albert.extension.python/modules
/usr/local/share/albert/org.albert.extension.python/modules
/usr/share/albert/org.albert.extension.python/modules
```

(Note: Double-clicking on a module in the settings will open the directory in the file manager.)

2. Clone this repository into your `modules` directory.

```bash
cd /path/to/modules

git clone https://github.com/DenverCoder1/timezone-convert-albert-ext.git
```

3. Ensure that `dateparser` is installed using pip.

```bash
python3 -m pip install dateparser
```

4. Enable the extension in the settings under `Extensions > Python`.

![settings](https://user-images.githubusercontent.com/20955511/142149401-188a865a-211e-4aa9-9e03-bf6314c2041e.png)

## Usage

Type a time, followed by the word "to" or "in" and then the timezone you want to convert to.

Examples:

`10pm PST to CST`

`8am MST in New York`

You can also use "Time in..." to convert the current time to another timezone.

`Time in UTC`

`Time in Tokyo`

## Configuration

In `config.jsonc` there are options to customize the extension:

### Date format

To change the way dates are displayed, set the `date_format` option.

The default is `%a %d %b` (e.g. "Mon 12 Dec").

See https://strftime.org for a list of supported formats

### Time format

To change the way times are displayed, set the `time_format` option.

You can use `%H:%M` for 24-hour time, or `%I:%M %p` for 12-hour time.

The default is `%I:%M %p` (eg. "12:00 PM")

See https://strftime.org for a list of supported formats

### Remove leading zeros

Set `remove_leading_zeros` to true to remove leading zeros from the date/time.

Eg. `Mon 01 Dec 01:00 PM` becomes `Mon Dec 1 1:00 PM`.

The default is `true`.

### Lowercase AM/PM

Set `lowercase_am_pm` to replace 'AM'/'PM' with 'am'/'pm' in time formats.

The default is `true`.

### Timezone aliases

To add a city or abbreviation as an alias for a timezone, add it to `tz_aliases` as a key-value pair.

See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a list of supported timezones


## Contributing

If you have any questions, suggestions, or issues, please feel free to open an issue or pull request.

## Support

💙 If you like this project, give it a ⭐ and share it with friends!

<p align="left">
  <a href="https://www.youtube.com/channel/UCipSxT7a3rn81vGLw9lqRkg?sub_confirmation=1"><img alt="Youtube" title="Youtube" src="https://custom-icon-badges.herokuapp.com/badge/-Subscribe-red?style=for-the-badge&logo=video&logoColor=white"/></a>
  <a href="https://github.com/sponsors/DenverCoder1"><img alt="Sponsor with Github" title="Sponsor with Github" src="https://custom-icon-badges.herokuapp.com/badge/-Sponsor-ea4aaa?style=for-the-badge&logo=heart&logoColor=white"/></a>
</p>

[☕ Buy me a coffee](https://ko-fi.com/jlawrence)
