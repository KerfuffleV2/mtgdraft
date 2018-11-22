# Use case

This tool assists with drafting cards in draft and sealed mode in the Magic: The Gathering Arena card game.

More information: https://magic.wizards.com/en/mtgarena

# Features

### Draft mode

You can enter card names (allows partial matches and tab completion) to see the tier list ratings. You enter sets of cards and then can see a list sorted by the ratings with information like cost/influence requirements visible.

##### Draft example:

![Draft example](https://raw.githubusercontent.com/KerfuffleV2/mtgdraft/assets/images/example-draft.png)

***

# Who it is useful for

Since it is a console-based application, it won't be useful for people that aren't comfortable at the commandline. It is a console-based Python script and should run on any platform Python 3 is supported (Linux, OS X, Windows, etc).

***

# How use it

The source code is freely provided.

You will need a relatively recent version of Python 3: https://www.python.org/

If you want to see colors, the Colorama package will need to be installed: https://pypi.org/project/colorama/

You will need to generate the data files that the application requires:

### Tierlist data

1. Run `python3 util/makemtgtl.py`. This will generate `mtgtier.csv` into the current directory if all goes well.

### MTG cards data

This step is optional - the data will be used to display card costs and color requirements. If skipped, only the card name will show.

1. Download the set data in JSON format from https://mtgjson.com/v4/ - "All Sets" is what you want, not "All Cards".
2. Run `python3 util/makemtgcards.py`. This will generate `mtgcards.csv`  into the current directory if all goes well.

Note that the JSON file is about 200MB and the entirety is loaded into memory during processing.

# Where to download

You can either clone the Git repo or download the latest version in ZIP format.

ZIP format download: https://github.com/KerfuffleV2/mtgdraft/archive/master.zip

# Credits

This application would be useless without the tier lists and data people have taken the time to create and make available.

The card data comes from https://mtgjson.com/

The tierlist data is extracted from https://www.mtgranks.com/ which uses the reviews that LSV created from https://www.channelfireball.com/tag/lsvs-set-review/

Thank you to those people and organizations!
