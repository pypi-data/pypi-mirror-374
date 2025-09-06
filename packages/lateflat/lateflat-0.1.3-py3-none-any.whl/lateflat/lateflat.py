import re
import shutil
from argparse import ArgumentParser
from pathlib import Path
from zipfile import ZipFile


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("root")
    parser.add_argument("--input", "-i", default="main.tex")
    parser.add_argument("--output_dir", "-od", default=None)
    parser.add_argument("--output", "-o", default="main.tex")
    parser.add_argument("--clean", "-c", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    # When specifying a directory path with spaces on Windows,
    # the path should be enclosed in quotation marks.
    #
    # However, if there is a trailing backslash,
    # it escapes the closing quotation mark, so it needs to be removed.
    #
    # Example: "parent\directory path\" -> args.root = parent\directory path"
    root = args.root.replace('"', "")

    if root.endswith("zip"):
        with ZipFile(root) as myzip:
            myzip.extractall(root.replace(".zip", ""))

    root_dir = Path(root.replace(".zip", ""))
    lines = flatten_with_input(args.input, root_dir=root_dir)

    if args.clean:
        lines = remove_comment(lines)

    if args.output_dir is None:
        output_dir = root_dir / "submit"
    else:
        output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    lines = flatten_images(lines, root_dir=root_dir, output_dir=output_dir)

    copy_supplementals(lines, root_dir=root_dir, output_dir=output_dir)

    with open(output_dir / args.output, "w", encoding="utf-8") as f:
        f.writelines(lines)


def flatten_with_input(filepath, root_dir: Path):
    filepath = root_dir / filepath

    lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\\input\{(.+)\}", line.strip())
            if m:
                input_filename = f"{m.group(1)}.tex"
                lines += flatten_with_input(input_filename, root_dir=root_dir)
            else:
                lines.append(line)

    return lines


def remove_comment(lines):
    return [line for line in lines if not line.strip().startswith("%")]


def flatten_images(lines, root_dir, output_dir):
    new_lines = []
    for line in lines:
        m = re.search(r"(\\includegraphics(\[.+\])?)\{(.+)\}", line)

        if not line.startswith("%") and m:
            image_path = m.group(3)
            image_filename = Path(image_path).name

            shutil.copy(root_dir / image_path, output_dir / image_filename)

            line = line.replace(m.group(0), f"{m.group(1)}{{{image_filename}}}")

        new_lines.append(line)

    return new_lines


def copy_supplementals(lines, root_dir: Path, output_dir: Path):
    for line in lines:
        m = re.match(r"\\bibliography\{(.+)\}", line)

        if m:
            filename = m.group(1)
            shutil.copy(root_dir / filename, output_dir / filename)
            continue

        m = re.match(r"\\documentclass(\[.+\])?\{(.+)\}", line)
        if m:
            filename = f"{m.group(2)}.cls"
            if (root_dir / filename).exists():
                shutil.copy(root_dir / filename, output_dir / filename)
            continue

        m = re.match(r"\\usepackage(\[.+\])\{(.+)\}", line)
        if m:
            filename = f"{m.group(2)}.sty"
            if (root_dir / filename).exists():
                shutil.copy(root_dir / filename, output_dir / filename)
            continue


if __name__ == "__main__":
    main()
