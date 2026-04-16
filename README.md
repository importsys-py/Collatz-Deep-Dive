Ecco il tuo testo sistemato solo nella grammatica e ortografia, senza cambiare il contenuto:

---

# Collatz-Deep-Dive

Advanced Collatz Conjecture toolkit with power-of-2 validation, negative cycle detection, and comprehensive logging. Built for performance and analysis.

# Collatz Conjecture explained

So what is Collatz's Conjecture? This conjecture states that if we take an integer number, odd or even, if it is odd we must multiply it by 3 and then add 1; otherwise, we divide it by 2 (3x + 1 | x / 2). As we know, for every number we have tested, the output will eventually always reach 4-2-1, creating a loop, because 4 / 2 results in 2; 2 / 2 results in 1; and 1 × 3 + 1 results in 4, forming a cycle.

We have tested numbers up to 2^68, but with this tool you can try almost any number, even very large ones. I have tried a very large number:
123214321414124256467688989123214321414124256467688989123214321414124256467688989123214321414124256467688989...

and the program returned the final cycle, the famous 4-2-1.

The conjecture has 3 rules:

1. The number must be an integer
2. If odd, use 3x + 1; if even, use x / 2
3. It functions only with positive numbers, as we have already seen

# Collatz Conjecture with negative numbers

The third rule says that the conjecture only works with positive numbers, but what happens if we try negative numbers? In this tool I created a function dedicated to negative numbers; I have already tested it and it works.

Let’s take -7 as an example to understand how it works:
-7 × 3 + 1 = -20
-20 / 2 = -10
-10 / 2 = -5
-5 × 3 + 1 = -14
-14 / 2 = -7

You can see it actually creates a loop, so we observe cyclic behavior. We can obtain loops similar to 4-2-1, but starting from different values.

However, this does not happen for every negative number. If we take -3, it will go like this:
-3 × 3 + 1 = -8
-8 / 2 = -4
-4 / 2 = -2
-2 / 2 = -1
-1 × 3 + 1 = -4

In this case, we reach a cycle different from the standard positive one. In negative numbers, sometimes we find loops and sometimes we do not.

Why does this happen? I am studying this conjecture (even though I am 16 years old) because it is simple but at the same time unpredictable. If we observe the distribution of numbers, it often appears chaotic, and we can go from low to high values in a single operation.

Some days ago I asked myself: what happens if instead of using 3x + 1, we use 3x - 1 on positive numbers? What we observe in negative numbers can also appear in positive numbers. For example:

7 × 3 - 1 = 20
20 / 2 = 10
10 / 2 = 5
5 × 3 - 1 = 14
14 / 2 = 7

So my question for everyone is: is it possible to define a unified version of the Collatz function that captures both the behavior of the standard 3x + 1 problem (on positive numbers) and its variations (such as 3x - 1 on negative numbers), and analyze whether they share common attractors or structural patterns?

# How to start the program

First, you need to install Python 3.9 or a later version from [https://www.python.org/](https://www.python.org/). After installing Python, restart your computer to ensure all changes are applied correctly. Once the system has restarted, open the Command Prompt (Windows) or a terminal (macOS and Linux), then install the required dependencies by navigating to the project folder.

On Windows, go to:
`C:\Users\yourname\Downloads\Collatz-Deep-Dive\other`
and run:
`pip install -r requirements.txt`

After that, navigate to the main source folder by typing:
`cd C:\Users\yourname\Downloads\Collatz-Deep-Dive\src`

Then run the program using:
`python congettura.py`
or, if Python is configured differently:
`py congettura.py`

On macOS and Linux, open the Terminal and install Python 3.9 or later from [https://www.python.org/](https://www.python.org/) or via your package manager, then restart your device if required. Navigate to the `other` directory:
`cd ~/Downloads/Collatz-Deep-Dive/other`

Then install dependencies:
`pip3 install -r requirements.txt`

After installation, move to the source directory:
`cd ~/Downloads/Collatz-Deep-Dive/src`

Finally, run:
`python3 congettura.py`

# Who am I?

My online name is importsyss. I am a Discord bot developer, turning 16 soon, and passionate about math, computer science, and physics. My goal is to learn AI (machine learning, deep learning, etc.) and become an AI engineer at a company, and obviously solve mathematical problems. I am not an especially intelligent person or anything like that; I simply want to discover and solve new math problems. If you want a Discord bot, write me on Discord @importsyss.
