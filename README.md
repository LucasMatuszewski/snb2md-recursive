# Convert Samsung S-Note .snb files to Markdown

`snb2md.py` is a simple Python script to convert **Samsung S-Note** `.snb` files to markdown `.md` text files. It extracts the embedded images from the `.snb` and converts the freehand drawings and images from `.zdib` format (which ordinary programs can't read) to `.png` format.

I modified original script written in Python2 by [Matthias S. Benkmann in his repository](https://github.com/mbenkmann/snb2txt).

I needed this script for my personal migration from S-Note to Obsidian (I also added `wikilinks` support with `-w` flag, but without this flag exported files can be used with any markdown compatible editor).

Second script (recursive) also supports conversion of multiple files to one `exported` folder.

Since this scripts were an ad-hoc solution for a one-time migration, it is neither perfect nor under active development but I'll be happy to include patches you send me, and you can also ask for modifications (maybe I will find time :)

It's safest to place these script files in the same directory you have your `.snb` files (but you may have also subdirectories with `.snb` files, recursive script supports that).

- [Download main script for one file](https://raw.githubusercontent.com/LucasMatuszewski/snb2md-recursive/master/snb2md.py)
- [Download recursive script to process many files](https://raw.githubusercontent.com/LucasMatuszewski/snb2md-recursive/master/snb2md-recursive.py)
  (requires the main script in the same directory)

# Usage

## snb2md.py

This script is used to convert a single **Samsung S-Note** `.snb` file to a markdown `.md` file. You can use it by typing in your console:

```shell
python snb2md.py [options] inputFile.snb
```

**Options**

- `inputFile.snb`: a path to file you want to convert to `.md`
- `-d` or `--dir`: directory to extract images (defaults to same directory as `.md` file)
- `-o` or `--output`: Specify the output markdown file name. If not provided, the `inputFile` name with a `.md` extension will be used
- `-w` or `--wikilinks`: Enable support for `[[wikilinks]]` in images (Markdown links by default)

## snb2md-recursive.py

This script is used to convert multiple **Samsung S-Note** `.snb` files to markdown `.md` files. It requires the snb2md.py script to be in the same directory. You can use it by typing in your console:

```shell
python snb2md-recursive.py [options] startingDirectory
```

**Options**

- `startdir`: Directory to start the recursive search for `.snb` files. If not provided, the current directory will be used.
- `-d` or `--dir`: directory to extract images (defaults to same directory as `.md` file)
- `-w` or `--wikilinks`: Enable support for `[[wikilinks]]` in images (Markdown links by default)

> Remember to replace `inputfile.snb` and `startingDirectory`, with your actual file or directory names.

# Dependencies

These scripts are written in **Python 3** and require Python 3 to be installed on your system. They also use several Python libraries, which are not included in Python standard library (`Pillow` and `unidecode`), but can be installed using **pip**:

```shell
pip install -r requirements.txt
```
