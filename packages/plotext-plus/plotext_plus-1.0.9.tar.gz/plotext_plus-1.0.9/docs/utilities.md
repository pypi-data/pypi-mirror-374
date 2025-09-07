# Utilities

- [Clearing Functions](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#clearing-functions)
- [Canvas Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#canvas-utilities)
- [File Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#file-utilities)
- [Testing Tools](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#testing-tools)
- [Command Line Tool](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#command-line-tool)
- [Colored Text](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#colored-text)
- [Docstrings](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#docstrings)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide)

## Clearing Functions

Here are all the available clearing functions:

- `clear_figure()`, in short `clf()`, clears **all internal definitions** of the subplot it refers to, including its subplots, if present; If it refers to the entire figure, it will clear everything.

- `clear_data()`, in short `cld()`, clears only the **data information** relative to the active subplot, without clearing all the other plot settings.

- `clear_color()`, in short `clc()`, clears only the **color settings** relative to the active subplot, without clearing all other plot settings. The final rendering of this subplot will be colorless. This function is equivalent to `theme('clear')`.

- `clear_terminal()`, in short `clt()`, clears the **terminal screen** and it is generally useful when plotting a continuous stream. If its `lines` parameter is set to an integer, only the specified number of lines will be cleared: note that, depending on the shell used, few extra lines may be printed after the plot.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#utilities)

## Canvas Utilities

These functions are useful to save or change how the final result is outputted.

- `interactive(True)` allows to **plot dynamically** without using the `show()` method. A new plot is shown automatically when a change is made.

- `build()` is equivalent to `show()` except that the final **figure is returned as a string** and not printed.

- `save_fig(path)` **saves** the colorless version of **the plot**, as a text file, at the `path` specified:
  
  - if the path extension is `.html` the colors will be preserved,
  - if `append = True` (`False` by default), the final result will be appended to the file, instead of replacing it,
  - if `keep_colors = True` (`False` by default), the `txt` version will keep the ansi color codes and in Linux systems, the command `less -R path.txt` can be used to render the colored plot on terminal.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#utilities)

## File Utilities

Access file utilities through the clean public API:

```python
import plotext_plus as plt
from plotext_plus import utilities as ut  # Clean public API

# File path utilities
script_dir = ut.script_folder()        # Get script directory
parent_dir = ut.parent_folder(path, level=1)  # Get parent folder
full_path = ut.join_paths('~', 'data', 'file.txt')  # Join paths with ~ expansion

# File operations
ut.save_text(text, path)              # Save text to file
data = ut.read_data(path, delimiter=' ', columns=[1,2], header=True)
ut.write_data(data, path, delimiter=',')  # Write matrix data
matrix_t = ut.transpose(matrix)       # Transpose matrix

# Download and cleanup
ut.download(url, path)                # Download from URL
ut.delete_file(path)                  # Delete file if exists
```

### Available Functions

- `script_folder()` - Returns the folder containing the script where it is run
- `parent_folder(path, level=1)` - Returns parent folder at specified level above
- `join_paths(*paths)` - Joins strings into proper file path (~ becomes home folder)  
- `save_text(text, path)` - Saves text content to specified path
- `read_data(path, delimiter=' ', columns=None, header=False)` - Reads numerical data from file
- `write_data(data, path, delimiter=' ', columns=None)` - Writes matrix data to file
- `transpose(matrix)` - Transposes a 2D matrix
- `download(url, path)` - Downloads content from URL to path
- `delete_file(path)` - Deletes file if it exists

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#utilities)

## Testing Tools

Here are some tools useful to test the `plotext_plus` package:

- `sin()` outputs a **sinusoidal signal** with the given `periods`, `length`, `amplitude`, `phase` and `decay` rate. More documentation is available using `doc.sin()`.

- `square()` outputs a **square wave signal** with the given n `periods`, `length` and `amplitude`. More documentation is available using `doc.square()`.

- `test()` to perform a **quick plotting test** (up to image rendering): it will download and finally remove a test image. 

- `time()` returns the **computation time** of the latest `show()` or `build()` function.

- A series of **test files** can be downloaded using the following url paths in conjunction with the `download()`method:
  
  - `test_data_url`  is the url of some 3 columns test data,
  - `test_bar_data_url` is the url of a simple 2 columns data used to test the `bar()` plot,
  - `test_image_url` is the url of a test image,
  - `test_gif_url` is the url of a test GIF image,
  - `test_video_url` is the url of a test video,
  - `test_youtube_url` is the url to a test YouTube video.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#utilities)

## Command Line Tool

There are two ways one could use `plotext_plus` directly on terminal. The first is by using its dedicated command line tool, to print a simple scatter, line, bar or histogram plot, as well as for image plotting, GIFs, video and YouTube rendering.  For further documentation run, on terminal:

```console
plotext_plus --help
```

![command-tool](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/command-tool.png)

The documentation of each function is also available. For example with:

```console
plotext_plus scatter --help
```

![scatter-tool](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/scatter-tool.png)

- The  `--path` option is used to read from the specified path.

- The `--lines` option is used to plot a long data table at chunks of given `LINES` (1000 by default). 

- The tool recognizes the keyword `test` as path, to internally downloads and finally remove some test file. Here are some example: 
  
  ```console
  plotext_plus scatter --path test --xcolumn 1 --ycolumns 2 --lines 5000 --title 'Scatter Plot Test' --marker braille
  plotext_plus plot --path test --xcolumn 1 --ycolumns 2 --sleep 0.1 --lines 2500 --clear_terminal True --color magenta+ --title 'Plot Test'
  plotext_plus plotter --path test --xcolumn 1 --ycolumns 2 --sleep 0.1 --lines 120 --clear_terminal True --marker hd --title 'Plotter Test'
  plotext_plus bar --path test --xcolumn 1 --title 'Bar Plot Test' --xlabel Animals --ylabel Count
  plotext_plus hist --path test --xcolumn 1 --ycolumns 2 --lines 5000 --title 'Histogram Test'
  plotext_plus image --path test
  plotext_plus gif --path test
  plotext_plus video --path test --from_youtube True
  plotext_plus youtube --url test
  ```

- you can type `python3 -m plotext_plus` (or `python -m plotext_plus` depending on your system) instead of `plotext_plus` on your terminal, if the command tool is not directly available.

- to allow TAB completion, install `plotext_plus` with flag `[completion]`, as explained [here](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#install). For issues on this feature, please report [here](https://github.com/ccmitchellusa/plotext_plus/pull/118). 

The second way to use `plotext_plus` directly on terminal requires the translation of a script into a single string and passing it to the `python3 -c` tool. For example:

```python
import plotext_plus as plt
plt.scatter(plt.sin())
plt.title('Scatter Plot')
plt.show()
```

translates into:

```console
python3 -c "import plotext_plus as plt; plt.scatter(plt.sin()); plt.title('Scatter Plot'); plt.show();"
```

- Each `python` line has to terminate with a semi-colon `;` and not a new line.

- Strings should be surrounded by the single quote `'` , while the double quote `"` should be avoided.

Each coded example in this [guide](https://github.com/ccmitchellusa/plotext_plus#guide) is followed by the correspondent direct terminal command line (of the second type).

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#utilities)

## Colored Text

Create colored terminal text using the `colorize()` method through the clean public API:

```python
import plotext_plus as plt
from plotext_plus import utilities as ut  # Clean public API

# Using clean utilities API
colored_text = ut.colorize("Hello World", color="red", style="bold", background="white")
print(colored_text)

# Direct printing (show=True)
ut.colorize("black on white, bold",        "black",        "bold",      "white",         show=True)
ut.colorize("red on green, italic",        "red",          "italic",    "green",         show=True)
ut.colorize("yellow on blue, flash",       "yellow",       "flash",     "blue",          show=True)
ut.colorize("magenta on cyan, underlined", "magenta",      "underline", "cyan",          show=True)

# Advanced color codes
ut.colorize("integer color codes",         201,            "default",   158,             show=True)
ut.colorize("RGB color codes",             (16, 100, 200), "default",   (200, 100, 100), show=True)

# Remove coloring
clean_text = ut.uncolorize(colored_text)
```

### Colorize Parameters

- `text` - The string to colorize
- `color` - Foreground color (name, integer, or RGB tuple)
- `style` - Text style ("bold", "italic", "underline", "flash", etc.)
- `background` - Background color (same formats as color)
- `show` - If True, prints directly instead of returning string

![colorize](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/colorize.png)

- The available color codes are presented [here](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/aspect.md#colors), while the available styles [here](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/aspect.md#styles).

- Using the `flash` style will result in an actual flashing string.

- To remove any coloring use the `uncolorize()` method.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#utilities)

## Docstrings

All main `plotext_plus` methods have a doc-string that can be accessed in three ways. For example the doc-string of the `scatter()` function can be accessed:

- as usual, using `print(scatter.__doc__)`, for its uncolorized version, 

- more easily through the `doc` container, using `doc.scatter()`, for its colorized version,

- similarly with its internal .doc() method with `scatter.doc()`, for its colorized version,

- with `doc.all()` which prints all `plotext_plus` colorized doc-strings.

Here are some methods that directly output some useful `plotext_plus` guides:

- the `markers()` method displays the available **marker codes**, also discussed  [here](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/aspect.md#markers),

- the `colors()` method displays the available **color codes**, also discussed [here](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/aspect.md#colors),

- the `styles()` method displays the available **style codes**, also discussed [here](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/aspect.md#styles),

- the `themes()` method displays the available **themes**, also discussed [here](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/aspect.md#themes).

Finally the `platform` string will return your OS (Unix or Windows) and `version`, the `plotext_plus` version installed. 

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Utilities](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/utilities.md#utilities)
