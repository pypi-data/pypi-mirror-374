# Notes

- [Install](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#install)
- [Future Ideas](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#future-ideas)
- [Updates](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#updates)
- [Credits](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#credits)
- [Similar Projects](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#similar-projects)


[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide)

## Install

### Quick Installation

For most users, install plotext with:

```bash
pip install plotext
```

### Modern Python Development (Recommended)

Using **UV** (modern Python package manager):

```bash
# Install plotext_plus
uv add plotext_plus

# Install with image support
uv add "plotext_plus[image]"

# Install with video support  
uv add "plotext_plus[video]"

# Install with all features
uv add "plotext_plus[image,video,completion]"
```

### Traditional pip Installation

```bash
# Basic installation
pip install plotext_plus

# Upgrade to latest version
pip install plotext_plus --upgrade

# Install with optional features
pip install "plotext_plus[image]"      # Image plotting (PNG, JPG, GIF)
pip install "plotext_plus[video]"      # Video rendering (MP4, YouTube)
pip install "plotext_plus[completion]" # TAB completion for CLI tool
```

### Development Installation

Install from source for the latest features:

```bash
# Using UV (recommended)
uv add "git+https://github.com/ccmitchellusa/plotext_plus.git"

# Using pip
pip install git+https://github.com/ccmitchellusa/plotext_plus.git
```

### Optional Dependencies

- **pillow** - Image plotting (PNG, JPG, GIF support)
- **opencv-python** - Video rendering and processing
- **ffpyplayer** - Audio streaming for videos
- **pafy** and **youtube-dl** - YouTube video streaming
- **shtab** - TAB completion for command line tool

### Testing Installation

Verify your installation works correctly:

```python
import plotext_plus as plt
plt.test()  # Downloads and displays a test image, then removes it
```

### Platform Support

- **Tested on**: Ubuntu 22.04, macOS, Windows 10/11
- **Python versions**: 3.7+ (3.10+ recommended)
- **Terminal requirements**: Any modern terminal with Unicode support

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Notes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#notes)

### New Features being considered for future versions

- add custom lines, as requested in issue [Issue 145](https://github.com/ccmitchellusa/plotext_plus/issues/145)
- support datetime integration, as requested in issue [Issue 154](https://github.com/ccmitchellusa/plotext_plus/issues/154)
- add command line arguments to set plot limits, as requested in issue [Issue 173](https://github.com/ccmitchellusa/plotext_plus/issues/173)
- allow plot and scatter to start from 0 and not 1 (optionally), as requested in issue [Issue 176](https://github.com/ccmitchellusa/plotext_plus/issues/176)
- add heatmap plot, as requested in issue [Issue 143](https://github.com/ccmitchellusa/plotext_plus/issues/143)
- add OHLC date time plot, as requested in issue [Issue 149](https://github.com/ccmitchellusa/plotext_plus/issues/149)
- add network graphs, as requested in issue [Issue 160](https://github.com/ccmitchellusa/plotext_plus/issues/160)
- integrate `colorize()` in `text()` and `indicator()` or or any string `label` parameter, as requested in issue [Issue 144](https://github.com/ccmitchellusa/plotext_plus/issues/144); possible idea: `colorize()` to output a `matrix_class()` object
- allow simple bar plots in matrix of subplots, as requested in issue [Issue 171](https://github.com/ccmitchellusa/plotext_plus/issues/171); this could be possibly extended to allow images also, rendered with fast parameter set to `True`
- allow user to decide plot legend position and frame
- allow clickable plots, as requested in issue [Issue 175](https://github.com/ccmitchellusa/plotext_plus/issues/175); this sounds hard!
- add text table feature, with nice formatting (?)

### New Functions

- add `bold()` function, to make a string bold
- add `plotter()` function, to scatter and plot at the same time
- add `clear_settings()` method to clear only the plot settings (labels, title and so on) and not the data, or colors
- add `simple_hist()` function, analogous to `simple_bar()`


### General Improvements

- add uppercase, lowercase and title styles
- add log parameter to `save_fig()` and similar
- no float in axes labels if ticks are all integers
- catch errors in video reproduction and get youtube
- in read data, default folder should be script folder
- allow simple bar plots to handle negative values
- allow `limit_size()` to be used also after `plot_size()`
- add bar `alignment` and `style` parameter
- add matrix plot side bar, to connect intensity level with actual matrix value
- high resolution markers available on Windows and other rarer terminals (under request and not sure how)
- add method to optionally set the sizes of a matrix of subplots giving priority to the subplots closer to bottom right edge, instead of upper left ones (as by default)
- convert the class `matrix_class()`, the engine running the plots, in C++ and connect it to the Python code (not sure how and would appreciate some help on this)


### Internal Conventions

- change candlestick data name conventions
- add parameter on bar plot methods for custom texts above bars, as proposed in [Pull Request 164](https://github.com/ccmitchellusa/plotext_plus/pull/164)
- unify name for `color` and `colors` parameters in `candlestick()`, `multiple_bar()` etc ...
- change `coordinate` parameter to `x` and `y` in `hline()` and `vline()`
- change `strings_to_time()` to `strings_to_times()`
- decide general convention for method aliases
- change `frame` parameter to `show` in `frame()` method
- change count from 0 in command line tool `xcol` and `ycols` parameters, for uniformity

### Documentation and Testing

- add docstring for `string_to_time()` and `strings_to_times()`
- add unit testing, as suggested in [Issue 130](https://github.com/ccmitchellusa/plotext_plus/issues/130)
- extend command line tool so that `man plotext` and `whatis plotext` are allowed

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Notes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#notes)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Notes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#notes)

## Credits

From [Pull requests](https://github.com/ccmitchellusa/plotext_plus/pulls):

- [cwaldbieser](https://github.com/cwaldbieser) for the `first_row` parameter idea in the `read_data()` method in [Pull Request 166](https://github.com/ccmitchellusa/plotext_plus/pull/166)
- [luator](https://github.com/luator) for fixing legend symbol for braille markers in [Pull Request 135](https://github.com/ccmitchellusa/plotext_plus/pull/135)
- [luator](https://github.com/luator) for fixing legend symbol for braille markers in [Pull Request 135](https://github.com/ccmitchellusa/plotext_plus/pull/135)
- [Freed-Wu](https://github.com/Freed-Wu) for introducing TAB completions to the command line tool in [Pull Request 118](https://github.com/ccmitchellusa/plotext_plus/pull/118) 
- [pankajp](https://github.com/pankajp) for allowing `plotext` to be used with `python3` with `-m` flag in [Pull Request 107](https://github.com/ccmitchellusa/plotext_plus/pull/107)
- [soraxas](https://github.com/soraxas) for functionality that accounts for exponential float notation in [Pull 82](https://github.com/ccmitchellusa/plotext_plus/pull/82)

From [Issue Reports](https://github.com/ccmitchellusa/plotext_plus/issues):

- [luator](https://github.com/luator) for requesting `marker` parameter in the `from_matplotlib()` method in [Issue 134](https://github.com/ccmitchellusa/plotext_plus/issues/134)
- [darul75](https://github.com/darul75) for requesting multiple lines in `text()` in [Issue 127](https://github.com/ccmitchellusa/plotext_plus/issues/127)
- [PhilipVinc](https://github.com/PhilipVinc) for `error()` plot idea, requested in [Issue 122](https://github.com/ccmitchellusa/plotext_plus/issues/122)
- [darul75](https://github.com/darul75) for requesting a simple KPI indicator  in [Issue 121](https://github.com/ccmitchellusa/plotext_plus/issues/121)
- [Freed-Wu](https://github.com/Freed-Wu) for requesting interactive mode in [Issue 115](https://github.com/ccmitchellusa/plotext_plus/issues/115)
- [Freed-Wu](https://github.com/Freed-Wu) for requesting a better way to deal with `Nan` and `None` values in [Issue 114](https://github.com/ccmitchellusa/plotext_plus/issues/114)
- [3h4](https://github.com/3h4) for requesting confusion matrix in [Issue 113](https://github.com/ccmitchellusa/plotext_plus/issues/113)
- [dns13](https://github.com/dns13) for requesting `append` option in save_fig() function in [Issue 109](https://github.com/ccmitchellusa/plotext_plus/issues/109)
- [vps-eric](https://github.com/vps-eric) for requesting square waves in [Issue 108](https://github.com/ccmitchellusa/plotext_plus/issues/108)
- [newbiemate](https://github.com/newbiemate) for requesting simple bar functionality in [Issue 98](https://github.com/ccmitchellusa/plotext_plus/issues/98)
- [Neo-Oli](https://github.com/Neo-Oli) for requesting braille based markers in [Issue 89](https://github.com/ccmitchellusa/plotext_plus/issues/89)
- [pieterbergmans](https://github.com/pieterbergmans) for requesting reverse axes functionality in [Issue 86](https://github.com/ccmitchellusa/plotext_plus/issues/86)
- [MartinThoma](https://github.com/MartinThoma) for inspiring the idea behind `event_plot()` in [Issue 83](https://github.com/ccmitchellusa/plotext_plus/issues/83)
- [wookayin](https://github.com/wookayin) for requesting the back-end function `from_matplotlib()` in [Issue 75](https://github.com/ccmitchellusa/plotext_plus/issues/75)
- [NLKNguyen](https://github.com/NLKNguyen) for ideas inspiring the `horizontal_line` and `vertical_line` functions in [Issue 65](https://github.com/ccmitchellusa/plotext_plus/issues/65)
- [jtplaarj](https://github.com/jtplaarj) for the great ideas and codes regarding multiple and stacked bar plots in [Issue 48](https://github.com/ccmitchellusa/plotext_plus/issues/48)
- [asartori86](https://github.com/asartori86) for the awesome command line tool in [Issue 47](https://github.com/ccmitchellusa/plotext_plus/issues/47)
- [ethack](https://github.com/ethack) for  solving single bar error in[Pull 43](https://github.com/ccmitchellusa/plotext_plus/issues/43)
- [ethack](https://github.com/ethack) for  requesting log scale on bar plot in [Issue 37](https://github.com/ccmitchellusa/plotext_plus/issues/37)
- [gregwa1953](https://github.com/gregwa1953) for  inspiring `limit_size()` in [Issue 33](https://github.com/ccmitchellusa/plotext_plus/issues/33)
- [rbanffy](https://github.com/rbanffy) for suggestion of using 3 x 2 unicode mosaic box characters in [Issue 29](https://github.com/ccmitchellusa/plotext_plus/issues/29).
- [henryiii](https://github.com/henryiii) for unit-test suggestion in [Issue 32](https://github.com/ccmitchellusa/plotext_plus/issues/32)
- [whisller](https://github.com/whisller) and [](https://github.com/willmcgugan` for integration with `Rich` package in [Issue 26](https://github.com/ccmitchellusa/plotext_plus/issues/26)
- [garid3000](https://github.com/garid3000) for the idea of a function that returns the plot canvas in [Issue 20](https://github.com/ccmitchellusa/plotext_plus/issues/20)
- [robintw](https://github.com/robintw) and [](https://github.com/Sauci` for horizontal bar plot idea and code, respectively in [Issue 16](https://github.com/ccmitchellusa/plotext_plus/issues/16)
- [Zaneo](https://github.com/Zaneo) for multiple data set idea in [Issue 13](https://github.com/ccmitchellusa/plotext_plus/issues/13)
- [Zaneo](https://github.com/Zaneo) for double axes idea in [Issue 12](https://github.com/ccmitchellusa/plotext_plus/issues/12)
- users [geoffrey-eisenbarth](https://github.com/geoffrey-eisenbarth) and  [matthewhanson](https://github.com/matthewhanson) for requesting datetime support in [Issue 7](https://github.com/ccmitchellusa/plotext_plus/issues/7)
- [kris927b](https://github.com/kris927b) for requesting histogram plot in [Issue 6](https://github.com/ccmitchellusa/plotext_plus/issues/6)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Notes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#notes)

## Similar Projects

These count as well as source of inspiration:

- [plotille](https://github.com/tammoippen/plotille)
- [termplot](https://github.com/justnoise/termplot)
- [termgraph](https://github.com/sgeisler/termgraph)
- [terminalplot](https://github.com/kressi/terminalplot)
- [asciichart](https://github.com/cashlo/asciichart)
- [uniplot](https://github.com/olavolav/uniplot)
- [bashplotlib](https://github.com/glamp/bashplotlib)
- [termplotlib](https://github.com/nschloe/termplotlib)
- [termgraph](https://github.com/mkaz/termgraph)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Notes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/notes.md#notes)
