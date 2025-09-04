update `setup_voice` in `cli_commands.py` with the new options like ``


1. replace `--config` cli with `--config-show`
2. add new cli option `-c <config.json>` & `--config <config.json>` so the user can specify config location


add a new `-l <log.md>` & `--log <log.md>` cli option that create a markdown append log with the following format:

```
## 2025-09-01T11:26:27
Test one, two, three.

## 2025-09-02T12:26:27
Another test transcription.
```

You should create a helper function to produce the output `to_log_format(content="", stylize=False)`. If `stylize` then the date should be stylized like so `[dim][white]## [/white][blue]2025-09-02T12:26:27[/blue][/dim]` for printing in the terminal.


refractor `ConfigManager` initialization in `cli.py` so we are not duplicating logic. and so cli args like `our_args.log` are set and override the default and/or set config.json value.

```py
def main() -> int:
    ...
    our_args, bin_args = parser.parse_known_args()
    config_manager = ConfigManager(Path(our_args.config) if our_args.config else None)

```


`cli.py` is gettting a bit long, what's the best way's in python to break up logic like this. explain +/- of each approach


`cli.py` is gettting a bit long, lets refractor a bit:

1. cli.py (entry point) - argument parsing + main()
2. new `cli_commands.py` - setup_voice, test_voice, show_config
3. new `cli_utils.py` - shared UI helpers
4. `run_with_bin` into  core.py where it better suited



Can you look through the code again and update the README? There's a handful of missing options that are not reflected there yet. And then proofread/edit, don't make me sound like a robot corporate shill

Update the default `-b, --binary` command to permit binary or binary-less running of `code_speak`. An empty string or null value in the config would be binary-less for example `{"code_speak": {"binary": ""}}`. That is, unless a binary is defined in the config or cli arguments assume binary-less operation.

+ If running in binary-less mode, and `--help` passed it should show the help/cli arguments for `code_speak`






Create a new config option called `replace` along with a new file `replace.py` to handle the new logic. The goal is to allow users to easily create and define a custom set of regex replace rules. either an key/value pair object or an array of filepaths that lead to key/value pair object json files like `{"replace": ["/replace/number.json", "/replace/letters.json"]}`. limit the scope to what's possible via `re`.

## key/pair format

##### simple string
```
{
  "replace": {
    "example": "EXAMPLE",
    " white space ": " WHITESPACE "
  }
}
```

##### regex key with string replace

```
{
  "replace": {
    "\\s*question\\s*mark\\.?": "?",
    "\\s*exclamation\\s*mark\\.?": "!"
  }
}
```

##### regex key (with option `/<regex>/[options]`) with string 

```
{
  "replace": {
    "/(\\s+)(comma)(\\s+)/gmi": ", "
  }
}
```

##### regex key with substitution groups

```
{
  "replace": {
    "/(\\s+)(comma)(\\s+)/gmi": ",\\g<3>",
    "(\\s+)(semi)(\\s+)": ";\\g<3>"
  }
}
```

##### regex anchored with string 

```
{
  "replace": {
    "/^start/i": "START",
    "/end$/i": "END"
  }
}
```




exclamation mark

A vector logo illustration against a plain white background of stylized 3d text that create the shape of a recognizable microphone silhouette and read  "CODE" - as if the letters themselfs made microphone with their with cyber-punk mesh grid gradients

A vector logo illustration against a plain white background of the word "CODE" in stylized 3d text that shape a recognizable microphone silhouette.

A vector logo illustration against a plain white background of the word "CODE" rotated vertically with the 'C' at the bottom and 'E' at the top. The letters form the shape of an audio microphone as if the letters created the micropone cone

A vector logo illustration against a plain white background of vertical rotated text "CODE" . The letters form the shape of an audio microphone as if the michropone cone was cyber-punk edged with phat "CODE" letters and code-speak vibes

A 3D vector logo illustration  render of a vintage microphone with the words "CODE" and "SPEAK" vertically inlaid and integrated into its sides, featuring the same gradient and mesh texture as the microphone. The words should be centered and legible, with a slight depth effect. The overall image should have a modern, sleek aesthetic with soft, studio-like lighting. The background should be a clean, minimalist white.


A vector logo illustration

A vector logo illustration against a plain white background of the word "CODE" rotated vertically with the 'C' at the bottom and 'E' at the top. The letters morph into the shape of an audio microphone silhouette

A vector logo illustration against a plain white background of the word "CODE" that reads vertically with the 'C' at the bottom and 'E' at the top - in other words: as if rotate(90deg) applied. The letters have a linear gradient from, where the letters create a recognizable microphone silhouette

A vector logo illustration against a plain white background of the word audio microphone where the microphone forms the word "code" for code-speak vibes

A vector logo illustration against a plain white background of the word "CODE" that reads vertically - i.e: rotate(90deg) in CSS terms. The letters have a linear gradient from, where the 'C' transforms into the microphone base and 'ODE' create a recognizable microphone silhouette

rotated 90 degrees to read vertically, with each letter exhibiting a gradient of colors. The letters are stylized to resemble a microphone, with the top half curving inward and the bottom half curving outward to create a recognizable microphone silhouette.


A vector logo illustration against a plain white background of the word "CODE" rotated 90 degrees to read vertically, with each letter exhibiting a gradient of colors. The letters are stylized to resemble a microphone, with the top half curving inward and the bottom half curving outward to create a recognizable microphone silhouette.

the word "code" in the shape of an audio microphone cone that gives code-speak vibes

uv tool install .

 the top arc, the 'O' is a full circle, the 'D' is an inverted arc, and the 'E' forms the base. The overall shape of the vertical word 'CODE' 

clean-up and refine this A cyberpunk-style vector logo where the word "CODE" is rotated 90 degrees to read vertically. Where the design cleverly transforms the text into a microphone shape
