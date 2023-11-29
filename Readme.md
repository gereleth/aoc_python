# Advent of Code 

My python solutions for [Advent Of Code](https://adventofcode.com) tasks. Check out my [2022 repo](https://github.com/gereleth/AdventOfCode2022) too.

## Prerequisites

I ran this code on python 3.10.8. It might work on other python 3 versions too.

Create a virtual environment and install dependencies.

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Layout

Code for each day is in `src/year{y}/day{d}.py`.

Inputs use `advent-of-code-data` library.

## Usage

Solve all tasks:

```bash
python src/solve.py --year {year}
```

Solve particular day:

```bash
python src/solve.py --year {year} --day {day}
```

Other options:

- `--test` - run on test input
- `--day {day} --input {filepath}` - run on a specified input file

## Animations

Some days include code to produce matplotlib animations illustrating the solution.

You can see them by running

```bash
python src/dayX.py
```
