# lateflat

**lateflat** is a command-line tool to flatten a LaTeX project into a single root directory, simplifying organization for project submission.

## Features
- Merges all files in a LaTeX project into a single directory.
- Updates `\input` and `\includegraphics` paths for compatibility in the flattened structure.
- Supports easy integration into CI/CD pipelines for automated submission preparations.

## Installation
Requires Python 3.7 or higher. Install using:

```bash
pip install lateflat
```

## Usage
To flatten a LaTeX project (including the article file named main.tex):

```bash
lateflat <path_to_your_latex_project>
```

This will organize all files in <path_to_your_latex_project> into a single main article file along with supplementary files (such as images, .sty, .cls, and .bib) in a submission-ready directory.

Additionally, it can output a zipped version of the flattened project directory if needed, making it easy to submit as a single article file along with supplementary files.

## Example Directory Structure
Assume your original LaTeX project structure is as follows:
```
project/
├── main.tex
├── sections/
│   ├── intro.tex
│   ├── methods.tex
│   └── results.tex
├── figures/
│   ├── fig1.png
│   └── fig2.png
│── custom.sty
│── formatting.cls
└── references.bib
```

After running `lateflat project`, the structure will be flattened to:

```
project/
└──submit/
│   ├── main.tex # including contents of intro.tex, methods.tex and result.tex
│   ├── fig1.png
│   ├── fig2.png
│   ├── custom.sty
│   ├── formatting.cls
│   └── references.bib
└── other files
```

In this flattened structure, all files are moved to a single root directory (`submit`), with `\input` and `\includegraphics` paths in `main.tex` updated accordingly.

## License

This project is licensed under the terms of the Apache License. See [LICENSE](LICENSE) for details.

## Contributing

Feel free to contribute! Fork the repository, make a pull request, or open an issue to discuss potential features.

## Contact

Maintainer: [Nkzono99](mailto:j-nakazono@stu.kobe-u.ac.jp)

Repository: [GitHub - lateflat](https://github.com/Nkzono99/lateflat)
