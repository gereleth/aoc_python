# Advent of Code 

My python solutions for [Advent Of Code](https://adventofcode.com) tasks. 

I did some puzzles from 2015 to warm up for 2023. Check out my [2022 repo](https://github.com/gereleth/AdventOfCode2022) too. 

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

Inputs use [`advent-of-code-data`](https://pypi.org/project/advent-of-code-data/) library.
Export `AOC_SESSION` environment variable to get your own inputs.
I also export `AOC_DATA` to put input files into a folder here.

```bash
# env.sh
export AOC_SESSION=cafef00db01dfaceba5eba11deadbeef
export AOC_DATA=/path/to/this/folder/data
```

## Usage

Solve all tasks from a year:

```bash
python src/solve.py --year {year}
```

Solve particular day:

```bash
python src/solve.py --year {year} --day {day}
```

Other options:

- `--year {year} --day {day} --input {filepath}` - run on a specified input file

## Animations

Some days include code to produce animations illustrating the solution.

You can see them by running

```bash
python src/yearY/dayXvis.py
```

### 2023

<table>
    <tr>
        <td>
            <h3><a href="src/year2023/day01vis.py">Day 1</a></h3>
            <a href="outputs/2023-day01-trebuchet.png"><img src="outputs/2023-day01-trebuchet.png" height="200"></a>
        </td>
        <td>            
            <h3><a href="src/year2023/day02vis.py">Day 2</a></h3>
            <a href="outputs/2023-day02-cube-conundrum.png"><img src="outputs/2023-day02-cube-conundrum.png" height="200"></a>
        </td>
        <td>
            <h3><a href="src/year2023/day03vis.py">Day 3</a></h3>
            <a href="outputs/2023-day03-gear-ratios.png"><img src="outputs/2023-day03-gear-ratios.png" height="200"></a>
        </td>
    </tr>
</table>