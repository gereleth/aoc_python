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
python src/vis.py --year {year} --day {day}
```

### 2023

Animations made with pygame. I'm adding videos to this [youtube playlist](https://www.youtube.com/playlist?list=PLo8XMPR0L8PcIiGtLllA7r3llWXHP3I_7). Images link to videos (if uploaded, up to day 3 right now)

<table>
    <tr>
        <td>
            <h4><a href="src/year2023/day01vis.py">Day 1</a></h4>
            <a href="https://youtu.be/9hk2N5j0_YE"><img src="outputs/2023-day01-trebuchet.png" height="200"></a>
        </td>
        <td>            
            <h4><a href="src/year2023/day02vis.py">Day 2</a></h4>
            <a href="https://youtu.be/kaY-e_vGzg4"><img src="outputs/2023-day02-cube-conundrum.png" height="200"></a>
        </td>
        <td>
            <h4><a href="src/year2023/day03vis.py">Day 3</a></h4>
            <a href="https://youtu.be/6he5Wah7WBg"><img src="outputs/2023-day03-gear-ratios.png" height="200"></a>
        </td>
    </tr>
    <tr>
        <td>
            <h4><a href="src/year2023/day04vis.py">Day 4</a></h4>
            <a href="outputs/2023-day04-scratchcards.png"><img src="outputs/2023-day04-scratchcards.png" height="200"></a>
        </td>
        <td>        
            <h4><a href="src/year2023/day05vis.py">Day 5</a></h4>
            <a href="outputs/2023-day05-if-you-give-a-seed-a-fertilizer.png"><img src="outputs/2023-day05-if-you-give-a-seed-a-fertilizer.png" height="200"></a>    
        </td>
        <td>
            <h4><a href="src/year2023/day06vis.py">Day 6</a></h4>
            <a href="outputs/2023-day06-wait-for-it.png"><img src="outputs/2023-day06-wait-for-it.png" height="200"></a>  
        </td>
    </tr>
    <tr>
        <td>
            <h4><a href="src/year2023/day07vis.py">Day 7</a></h4>
            <a href="outputs/2023-day07-camel-cards.png"><img src="outputs/2023-day07-camel-cards.png" height="200"></a>
        </td>
        <td>  
        </td>
        <td>
        </td>
    </tr>
</table>
