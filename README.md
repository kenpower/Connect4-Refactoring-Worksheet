Class code: REFACTORING_26
Lab: refactor
Refactorings: Rename Function, Rename Variable, Replace Magic Number with Constant, Extract Function, Merge Loops, Replace Nested Conditional with Guard Clauses, Replace Primitive with Object

# Refactoring Lab: Connect Four

You are given a small, working, **smelly** implementation of Connect Four in `ConnectFour.h` / `ConnectFour.cpp`, with tests in `test.cpp`.

It works, but it is hard to read and hard to change.

Also the logic has a couple of **serious** limitations:

* `winner()` only recognises **horizontal** lines of four (vertical or diagonals are not wins!).
* The AI move choice is naïve: *win if you can, otherwise play anywhere*.

Your job is to:
1. **refactor** the code (make it clearer without changing what it does) until adding the missing features becomes easy.
2. Then you use TDD to add the missing features (proper win test, smarter move choice).

### The two hats

You will switch between two kinds of work. Every step that changes code is labelled **[Refactor]** or **[Develop]** to tell you which hat it needs.

|Label|What you're doing|What the tests should do|
|-|-|-|
|**[Refactor]**|Changing the *structure* of the code, not its behaviour|Stay **green** the whole time|
|**[Develop]**|Changing *behaviour* (new feature or new rule)|Write a test that goes **red**, then make it **green**|

Never wear both hats at once. If you are refactoring and a test goes red, you have changed behaviour by accident: **undo** and take a smaller step.

### How the board is stored

The board is a `std::string` of 42 characters: 6 rows of 7, **top row first**. `'-'` is empty; `'X'` and `'O'` are pieces. Pieces drop to the lowest empty cell in a column.

```
 column:  0123456
 row 0    -------      <- top
 row 1    -------
 row 2    -------
 row 3    -------
 row 4    OOO----
 row 5    XXXX---      <- bottom: X has won
```

In the tests, the `rows(...)` helper lets you write boards exactly like this:

```cpp
rows("-------",
     "-------",
     "-------",
     "-------",
     "OOO----",
     "XXXX---")
```

### Working as a pair

* Work on **one machine** together. Only one of you needs the project built and running.
* **Driver** types; **navigator** reads the instructions, thinks ahead and spots mistakes.
* **Swap roles after every commit**: swap seats, not laptops.
* **Commit after every green step**, with a message that names the refactoring and what it changed:

  ```
  git commit -am "Rename Function: move -> bestMoveFor"
  ```

  For a **[Develop]** step, say what the code does now: `"Develop: any legal move, not just the first"`. Small commits mean that if you break something, you can always get back to the last green state.
* **To undo**, throw away everything you've changed in the code since your last commit:

  ```
  git restore Connect4-Tests
  ```

  This only touches the code folder, so your notes in `smells.md` are safe. There's no way to get the discarded changes back, which is why you commit after every green step.

### Time guide

The lab is **one hour** not including setup.

|Section|Type|Roughly|
|-|-|-|
|0. Setup|**Before the lab**|15 min, at home|
|1. Smells|Core|5 min|
|2. Easy changes|Core|15 min|
|3. Fuse the loops|Core|20 min|
|4. Magic numbers and duplication (4.1, 4.2)|Core|15 min|
|4.3 and 5. More ways to win|If you have time|20 min|
|6. A smarter player|Take-home, optional|40+ min|

Each round of change → run tests → commit → swap takes about 3 minutes. If a step takes much longer, ask for help rather than pushing on.

---

## 0. Setup 

Clone your repo and open it in your IDE. Build it and run the tests.

You're ready when you can build, see the 14 tests pass, and see the RedGreenGo game open. 

Do not change any code until you see all passing tests.

The project uses **CMake** and **GoogleTest**, and builds on Windows and Linux. You can use **Visual Studio 2022 or later**, **CLion**, **VS Code**, or the command line. There is no `.sln` file: open the repo **folder** in your IDE. GoogleTest downloads automatically the first time, so you need internet access.

**Follow the steps for your setup in [BUILD.md](BUILD.md).** In short:

* **Visual Studio:** *File → Open → Folder*, wait for CMake to finish, *Build → Build All*, then *Test → Run All Tests*.
* **CLion:** *File → Open* the folder, then run the **All CTest** configuration (not the green ▶ next to a test: RedGreenGo can't see those runs).
* **VS Code:** install the *C/C++* and *CMake Tools* extensions, open the folder, pick a kit, build, then run the tests from the **Testing** view.
* **Command line:** `cmake -S . -B build && cmake --build build && ctest --test-dir build`

All **14** tests should pass. **If they don't, ask for help before going any further.**

> Each test looks like `TEST(WinnerTest, ThreeInARowIsNotAWin) { ... }`. The first name groups related tests together; the second says what the test checks. When a test fails, GoogleTest shows you both names, the line, and the expected and actual values.

### Start RedGreenGo

**RedGreenGo** is a game that coaches you through the lab. It watches your test runs, your code and your commits, and tells you when to run the tests, commit or undo. The helper that connects it to your project, `rgg_server.py`, is already in this repo.

1. Open a terminal in the repo folder (the one with `CMakeLists.txt`):
   * **Visual Studio:** *View → Terminal*.
   * **VS Code:** *Terminal → New Terminal*.
   * **CLion:** *View → Tool Windows → Terminal*.
2. Start the helper and **leave it running**:

   ```
   python rgg_server.py
   ```

   On Windows, if that opens the Microsoft Store or says Python isn't found, use `py rgg_server.py`. On Linux, use `python3 rgg_server.py`. It reads the class code from the top of this README, so you don't need to type it.
3. The game opens in your browser at **http://127.0.0.1:8000/**. 
4. Type both your names and click **Start Game**.

The helper only reads your files; it never changes them. When the lab starts, the game asks you to find the smells yourselves first (section 1). Then it walks you through this worksheet one step at a time: each card shows the step to do now, with the full text from this README underneath, and switches to the **[Develop]** hat for you when a step needs it. You'll mostly follow the game and come back here for the reflection questions and if you get stuck.

**At the start of the lab:** open the project, start the helper again (step 2), run all the tests, and click **Start Game**.

> **Nothing happens when you run the tests?** Check the helper's terminal. If it says `doesn't save test results`, ask for help. If it says `No test results yet`, run **all** the tests through Test Explorer, the Testing view or **All CTest**: the game can't see a single test run from the ▶ next to a `TEST(...)`.

---

## 1. Smells

A *smell* is something in the code that makes it harder to understand or change. Read all of `ConnectFour.cpp` together. For each method, can you say in one sentence what it does? For each loop, can you say what it loops over *in game terms* (rows? columns? cells?)

Look for these smells in particular:

|Smell|What it looks like|
|-|-|
|**Poor name**|A name that doesn't tell you what the thing *means*: `t`, `p`, `move()`|
|**Magic number**|A literal number whose meaning you have to work out: `7`, `5`, `4`|
|**Duplicated code**|The same idea written out more than once|
|**Long or tangled method**|A method doing several jobs at once|
|**Primitive obsession**|Using an `int` or `char` for something that deserves its own type|

📝 **Write down the smells you find** in the table in [smells.md](smells.md), with its line number in `ConnectFour.cpp`. The first two rows are filled in as examples; add **at least three** of your own (RedGreenGo waits for three before it shows its list). Leave the **Fixed in** column empty for now. Commit `smells.md` before you change any code.

At the end of the lab you will fill in **Fixed in** with the step that removed each smell.

---

## 2. Easy changes

Every step in this section is **[Refactor]**. Do them **one at a time**. After **each** one:

> ✅ Run the tests. Green? **Commit.** Red? **Undo** (`git restore Connect4-Tests`) and try again more carefully.

Use your IDE's **rename** command to rename a name everywhere it's used, including in `test.cpp`: put the cursor on the name and press **Ctrl+R, Ctrl+R** (Visual Studio), **Shift+F6** (CLion) or **F2** (VS Code). Renaming by hand is how bugs creep in.

- [ ] **2.1 [Refactor]** `move()` doesn't say what it does. Rename it to `bestMoveFor()`.
- [ ] **2.2 [Refactor]** Rename the one-letter variables in `play()` and `bestMoveFor()`.

  Give each one a name that says what it *means*. Use the rename command for each one, but commit them together:

  |Where|Old|New|
  |-|-|-|
  |`play()` and `bestMoveFor()` parameters|`c`, `p`|`column`, `player`|
  |`bestMoveFor()` loops|`i`|`column` (it's a column the player might drop a piece into)|
  |`play()`|`r`, `b`|`row`, `newBoard`|
  |`bestMoveFor()`|`t`|? (Hint: it's the game *after* something has happened.)|

  Leave the `r` and `c` in `winner()` for now.

- [ ] **2.3 [Refactor]** Name the two flag values: add constants `NoMove` and `Empty`.

  Two values in the code are really flags. Add a constant for each to the **`public:`** section of the class (the tests need to see them, so they can't go under `private:`):

  ```cpp
  static constexpr int NoMove = -1;     // "there is no move"
  static constexpr char Empty = '-';    // "this cell is empty"
  ```

  Use `NoMove` in place of the `-1`, and `Empty` everywhere `'-'` is used in `ConnectFour.cpp`. In `test.cpp`, change the `-1` in `FullBoardHasNoMove` to `ConnectFour::NoMove`.

  > Use `constexpr`, not plain `const`. A `static constexpr` member is a true compile-time constant and needs no separate definition in the `.cpp` file, even when a test macro like `EXPECT_EQ` takes it by reference.

- [ ] **2.4 [Refactor]** Extract `r * 7 + c` into a private method `indexOf()`.

  The expression `r * 7 + c` (row × width + column) appears **many** times. Extract it into a private method:

  ```cpp
  int indexOf(int row, int column) const;
  ```

  and use it in `play()` and `winner()`.

  > 💡 **Hint:** in `winner()` the expressions have an extra offset on the end, like `board[r * 7 + c + 1]`. The `+ 1` belongs to the column, so it becomes `board[indexOf(r, c + 1)]`.

- [ ] **2.5 [Refactor]** Extract the "is this column full?" check into a private method `canPlayIn()`.

  In `bestMoveFor()`, `board[column] == Empty` checks only *one* cell, yet it is really asking a question about the whole column. 🤔 **Which cell is it checking, and why is that enough?** Extract it into a private method with a name that says what it *means*:

  ```cpp
  bool canPlayIn(int column) const;
  ```

  Use it in **both** loops.


---

## 3. Fuse the loops

After the easy changes, `bestMoveFor()` should look roughly like this:

```cpp
int ConnectFour::bestMoveFor(char player) const {
    for (int column = 0; column < 7; column++) {          // loop 1: look for a win
        if (canPlayIn(column)) {
            ConnectFour afterMove = play(column, player);
            if (afterMove.winner() == player)
                return column;
        }
    }
    for (int column = 0; column < 7; column++) {          // loop 2: any legal move
        if (canPlayIn(column))
            return column;
    }
    return NoMove;
}
```

Both loops visit the same seven columns. **Fusing** them means combining them into one loop. You can't just paste one into the other, though, because **both loops `return` early**. A loop that returns early stops the code after it from ever running, so moving it changes behaviour.

> **When is it safe to fuse two loops?** When they loop over the same range, and **neither** loop exits early or depends on something the other loop works out.

So first remove the early exits, one loop at a time. **Tests must stay green after every step.**

### Step 3.1 [Refactor]: loop 2 records its answer instead of returning it

```cpp
int defaultMove = NoMove;
for (int column = 0; column < 7; column++) {
    if (canPlayIn(column) && defaultMove == NoMove)
        defaultMove = column;
}
return defaultMove;
```

The `defaultMove == NoMove` check keeps the **first** playable column, exactly as the old `return` did. Run the tests: green? Commit.

### Step 3.2 [Refactor]: loop 1 does the same

```cpp
int winningMove = NoMove;
for (int column = 0; column < 7; column++) {
    if (canPlayIn(column) && winningMove == NoMove) {
        ConnectFour afterMove = play(column, player);
        if (afterMove.winner() == player)
            winningMove = column;
    }
}
```

Now neither loop returns. After both loops, choose the answer:

```cpp
if (winningMove != NoMove)
    return winningMove;
return defaultMove;
```

🤔 The original code had a third line, `return NoMove;`. Why don't we need it? Run the tests: green? Commit.

### Step 3.3 [Refactor]: fuse

The two loops now have the same header and no early exits, so it's safe. Move the body of loop 2 into loop 1 and delete loop 2. Run the tests: green? Commit.

### Step 3.4 [Develop]: change of hat. Simplify the default move

The rules only say *"if you can't win, play **any** legal move"*. We don't care **which** one. So the `defaultMove == NoMove` guard is doing work nobody asked for. **Delete it** (keep `canPlayIn(column)`).

This **changes behaviour**: `defaultMove` is now the *last* playable column instead of the first. Run the tests.

> ⚠️ **Two tests are expected to go red here:** `ChooseMoveTest.NoWinPicksFirstOpenColumn` and `ChooseMoveTest.SkipsFullColumn`. **Don't undo.**
>
> 🤔 The code still obeys the rules, so why are the tests failing? The tests check for **one particular** legal move when the rules allow **any** legal move. That's an **over-specified** test: it locks in a detail nobody cares about, and blocks a perfectly good change.
>
> **Fix the tests, not the code.** Rename `NoWinPicksFirstOpenColumn` to `NoWinPicksAValidColumn`. Store the move in a variable, then check it's a real column:
>
> ```cpp
> int move = game.bestMoveFor('X');
> EXPECT_GE(move, 0);
> EXPECT_LT(move, 7);
> ```
>
> In `SkipsFullColumn`, do the same, and also check the move is **not** column 0 (`EXPECT_NE(move, 0)`).

Green again? Commit.

### Step 3.5 [Refactor]: one variable, one exit

You now have two variables and some `if`s to choose between them. Simplify to a **single** `result` variable:

* If a column is not playable, skip it (`continue`).
* If playing the column wins, you can `return column;` straight away. Nothing beats a win, so stopping early is fine.
* Otherwise, remember it: `result = column;`.
* After the loop, `return result;`.

> ⚠️ **Start `result` at `NoMove`**, not at `0`. On a full board no column is playable, so the loop never sets `result`, and the method must still return "no move". If you start it at `0` (or leave it uninitialised), `ChooseMoveTest.FullBoardHasNoMove` goes red.

The whole method should now fit in about 10 lines. Run the tests: green? Commit.


---

## 4. Magic numbers and duplication

Every step in this section is **[Refactor]**. Steps 4.1 and 4.2 are core; 4.3 is for pairs who have time.

Look back at your smell list. **Which part of the code smells worst now?**

It is probably `winner()`. It's full of magic numbers, and the `'X'` check and the `'O'` check are copies of each other.

### Step 4.1 [Refactor]: name the numbers

Add these to the **`public:`** section of the class, next to `NoMove` (public, so the tests can use them too):

```cpp
static constexpr int Rows = 6;
static constexpr int Columns = 7;
static constexpr int WinLength = 4;
```

Replace the magic numbers **one kind at a time**. Run the tests and commit after each kind (in RedGreenGo, choose **Committed, but step 4.1 isn't finished yet** until the last one):

* every `7` → `Columns`
* the `6` in `winner()` → `Rows`
* the `5` in `play()` → ?  (*It's the bottom row. How do you write that using `Rows`?*)

Then look at `c < 4` in `winner()`.

> **Careful!** Is that `4` the same thing as `WinLength`? Try it with a bigger board: on a 10-column board, what should the limit be? It's actually `Columns - WinLength + 1`, which just *happens* to equal 4 here. One literal hiding two different meanings is exactly why magic numbers are dangerous.

### Step 4.2 [Refactor]: remove the X/O duplication

First, rename `r` → `row` and `c` → `column` in `winner()`, so the code below matches yours. Then add a helper that reads a cell:

```cpp
char cellAt(int row, int column) const;   // returns board[indexOf(row, column)]
```

Then, instead of checking for `'X'` and then for `'O'`, read the **first** cell of the four. If it's not `Empty`, check that the other three **match it**:

```cpp
char first = cellAt(row, column);
if (first != Empty && cellAt(row, column + 1) == first && /* ... */)
    return first;
```

Half of `winner()` disappears. Run the tests: green? Commit.

### Step 4.3 [Refactor]: turn "four in a row" into a loop (if you have time)

The `+1`, `+2`, `+3` offsets are really "step 1, 2, 3 along the line". Extract a method that checks **one line of `WinLength` cells**, starting at a cell and stepping in a direction:

```cpp
// Returns the player who owns this whole line, or Empty if nobody does.
char lineOwner(int row, int column, int rowStep, int columnStep) const;
```

For a horizontal line, `rowStep` is `0` and `columnStep` is `1`. Inside, use a loop over `step = 1 .. WinLength - 1` in place of the `+1, +2, +3`.

The line might run **off the edge of the board**, so add one more helper and check it before reading each cell:

```cpp
bool isOnBoard(int row, int column) const;
```

With that check in place, `winner()` can simply try **every** cell (`column < Columns`) and let `lineOwner()` reject lines that don't fit.

> The test `WinnerTest.LineDoesNotWrapAroundTheEdge` protects you here. In the string, the last cell of one row sits right next to the first cell of the next. Forget the bounds check and that test goes red.
>
> In a Visual Studio **Debug** build you may see a crash ("string subscript out of range") instead of a red test: on the bottom row, a line without the bounds check reads past the end of the string. It's the same mistake, so the fix is the same.

Run the tests: green? Commit.



---

## 5. More ways to win (if you have time)

This section needs step 4.3 done first.

We're still not playing real Connect Four: you can also win **vertically** and on **both diagonals**.

### Step 5.1 [Develop]: tests first

Write these four tests in the `WinnerTest` group. Use the `rows(...)` helper so you can *see* each board. **Run them and watch them fail** (all except the last one, which should already pass. Why?) Don't commit yet: with failing tests this isn't a green step. Go straight on to 5.2 and commit when everything passes (in RedGreenGo, then press **Skip** past 5.2).

|Test|Board idea|Expect|
|-|-|-|
|`VerticalFourIsAWin`|four `X` stacked in one column|`'X'`|
|`DiagonalUpRightIsAWin`|four `X` climbing `/` from bottom-left|`'X'`|
|`DiagonalUpLeftIsAWin`|four `O` climbing `\` from bottom-right|`'O'`|
|`DiagonalDoesNotWrapAroundTheEdge`|`X` at (row 0, col 6), (2,0), (3,1), (4,2)|`'-'`|

> 🤔 For the last test, work out the string positions of those four cells. What do you notice? What would a "lazy" diagonal check get wrong?

### Step 5.2 [Develop]: make them pass

If section 4 went well, this should be a **small** change. A line can run in four directions:

```cpp
const int Directions[][2] = {
    {0, 1},    // horizontal: step right
    {1, 0},    // vertical: step down
    {1, 1},    // diagonal: step down and right
    {1, -1},   // diagonal: step down and left
};
```

In `winner()`, loop over these directions and call `lineOwner()` for each. Run the tests: green? Commit.

> 🤔 **Reflect:** How many lines did you have to change to add three new ways to win? How many would it have taken in the original code?
>
> 🤔 Your users now want **Connect Five** on a **9 × 7** board. What would you change?



---

## 6. A smarter player (take-home)

This section is optional, for after the lab. It needs section 5 done first.

So far, the player wins if it can and otherwise plays any legal move. It doesn't even notice when the opponent is about to win.

We'll give every move a **score**, and pick the move with the highest score. There is **one** scoring rule for this whole section:

|Score|Meaning|
|-|-|
|**100**|The move **wins** the game|
|**0**|The move lets the **opponent win** on their very next turn|
|**50**|Anything else|

Once moves have scores, a move is no longer just a column number. It is a column **and** a score. An `int` can't hold both: that's *primitive obsession*. Time for a class.

### Step 6.1 [Develop]: a `Move` class, with tests

Put this class in `ConnectFour.h`, above `ConnectFour`. Write tests for `isBetterThan()` **first**, in a new `MoveTest` group (use `EXPECT_TRUE` and `EXPECT_FALSE`): a higher score is better, an equal score is **not** better, and any real move is better than `Move::none()`.

```cpp
class Move {
public:
    Move(int column, int score);
    int column() const;
    int score() const;
    bool isBetterThan(const Move& other) const;
    static Move none();      // column = -1, score = -1: worse than any real move
private:
    int column_;
    int score_;
};
```

`Move` is a **value object**: it has getters but no setters, and once created it never changes.

> Your `MoveTest` tests won't even compile until the `Move` class exists. For tests written first, a compile error counts as red: add the class, and they should go green.

> 🤔 `none()` uses a bare `-1` for its column, the same magic number you replaced with `ConnectFour::NoMove` in step 2.3. Why can't `Move` use `ConnectFour::NoMove` here? (Look at which class is declared first.) Is that worth fixing?

### Step 6.2 [Refactor]: use `Move` inside `bestMoveFor()`

Add a public method `int scoreMove(int column, char player) const`. For now it returns **100** if the move wins and **50** otherwise.

Rewrite `bestMoveFor()` as "find the best `Move`", the same pattern as finding the largest number in a list:

```cpp
Move best = Move::none();
// for each playable column:
//     Move candidate(column, scoreMove(column, player));
//     if (candidate.isBetterThan(best)) best = candidate;
return best.column();
```

> 💡 `bestMoveFor()` **still returns an `int`**, so none of the existing tests need to change. `Move` is an internal detail. Callers don't need to know it exists.

Run the tests: green? Commit.

### Step 6.3 [Develop]: don't hand the opponent a win

Put these tests in a new `ScoringTest` group. Write them **first** and watch them fail:

1. `MoveThatLetsOpponentWinScores0`

   ```
   -------
   -------
   -------
   -------
   OOO----
   OXO-XOX
   ```

   `scoreMove(3, 'X')` should be **0**: X fills the gap at the bottom of column 3, and O plays on top of it to win. `scoreMove(4, 'X')` should be **50**.

2. `BlocksOpponentWin`

   ```
   -------
   -------
   -------
   -------
   X------
   OOO-XX-
   ```

   `bestMoveFor('X')` should be **3**.

3. `WinBeatsBlock`: a board where X can win in one column **and** O threatens another. X should take the win.

   > 🤔 This one probably passes straight away, before you change any code. Why? Is it still worth keeping?

Now make them pass. You will probably want:

* `char opponentOf(char player)`: `'X'` ↔ `'O'`
* `bool canWinNextTurn(char player) const`: is there **any** playable column where this player wins straight away?

In `scoreMove()`: play the move, then ask whether the **opponent** can win next turn on the resulting board.

> 🤔 You never wrote a rule that says "block the opponent". So why does `BlocksOpponentWin` pass? (Look at what every *other* column scores.)



### Further stretch [Develop] (pick any)

* **Prefer the centre.** Pieces in the middle columns take part in more possible lines. Among moves with equal scores, prefer the column nearest the centre. Can you do it by changing `scoreMove()` only? Which tests do you need to write first?

  > ⚠️ If you add a small centre bonus inside `scoreMove()`, `MoveThatLetsOpponentWinScores0` goes red: it expects `scoreMove(4, 'X')` to be **exactly 50**, and column 4 is next to the centre. That's the over-specified test problem from step 3.4 again. Decide what the test really cares about (a losing move scores **lower than** a safe one?) and change the test to check that, rather than an exact number. Or keep `scoreMove()` exact and break ties in `bestMoveFor()` instead.
* **Double threats.** A move that leaves you **two** different winning columns can't be blocked. Score it 90.

---

## Wrap-up

Go back to [smells.md](smells.md). In the **Fixed in** column, write the step that removed each smell (for example `2.3`), or `still there`. Are any smells left? Commit it.

---

# Submission

1. **One person in the pair** pushes your commits to your pair's GitHub repo, the one created for you by **classroom50** .
2. **Each person** answers **four** of the following questions in the Blackboard submission:

   1. **Collaboration:** What did you learn about working together with your partner? Were there any challenges you faced?
   2. **Communication:** How did you communicate your ideas to each other? What strategies were effective?
   3. **Code quality:** What did you learn about writing better code through this exercise? How can you apply these lessons in the future?
   4. **Learning outcomes:** What new skills or concepts did you learn from your partner? Did their perspective change your understanding of the material?
   5. **Feedback:** How did you give and receive feedback during the pairing? Was there anything you found particularly helpful or unhelpful?
   6. **Time management:** How did you manage your time together? Were there any time-related challenges?
   7. **Future improvements:** If you could do this pairing activity again, what would you change to make it more effective?
   8. **RedGreenGo:** How did the RedGreenGo app affect the way you worked? Did its prompts to run the tests, commit or undo change your habits? Was there a moment where it helped, or got in the way?
   
