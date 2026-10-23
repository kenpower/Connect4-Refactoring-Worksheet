Class code: REFACTORING_26
Lab: refactor

# Refactoring Lab: Connect Four

You are given a small, working, **smelly** implementation of Connect Four in `ConnectFour.h` / `ConnectFour.cpp`, with tests in `test.cpp`.

It works, but it is hard to read and hard to change

Also the logic has a couple of **serious** limitations:

* `winner()` only recognises **horizontal** lines of four (vertical or diagonals are not wins!).
* The AI move choice is naïve: *win if you can, otherwise play anywhere*.

Your job is to:
1. **refactor** the code (make it clearer without changing what it does) until adding the missing features becomes easy.
2. Then you use TDD to add the missing features (proper win test, smarter move choice).

### The two hats

You will switch between two kinds of work. Each step is labelled with the hat it needs.

|Hat|What you're doing|What the tests should do|
|-|-|-|
|**Refactoring**|Changing the *structure* of the code, not its behaviour|Stay **green** the whole time|
|**Development**|Changing *behaviour* (new feature or new rule)|Write a test that goes **red**, then make it **green**|

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

In the tests, the `rows(...)` helper lets you write boards exactly like this.

### Working as a pair

* **Driver** types; **navigator** reads the instructions, thinks ahead and spots mistakes.
* **Swap roles at the start of every section.**
* **Commit after every green step** (`git commit -am "Rename move to bestMoveFor"`). Small commits mean that if you break something, you can always get back to the last green state.

### Time guide

|Section|Type|Roughly|
|-|-|-|
|0. Setup|Core|5 min|
|1. Smells|Core|10 min|
|2. Easy changes|Core|30 min|
|3. Fuse the loops|Core|25 min|
|4. Magic numbers and duplication|Core|30 min|
|5. More ways to win|Core|20 min|
|6. A smarter player|**Stretch**|40+ min|


\---

## 0\. Setup

Build and run the tests **before changing anything**.

Do not type any code until you see a green tests

The tests use **GoogleTest**. Open the project, build it, open **TestExplorer** and run all the tests (in Visual Studio: **Test → Run All Tests**, then look in **Test Explorer**).

All **14** tests should pass. **If they don't, ask for help before going any further.**

> Each test looks like `TEST(WinnerTest, ThreeInARowIsNotAWin) { ... }`. The first name groups related tests together; the second says what the test checks. When a test fails, GoogleTest shows you both names, the line, and the expected and actual values.

\---

## 1\. Smells 🔍

A *smell* is something in the code that makes it harder to understand or change. Read all of `ConnectFour.cpp` together. For each method, can you say in one sentence what it does? For each loop, can you say what it loops over *in game terms* (rows? columns? cells?)

Look for these smells in particular:

|Smell|What it looks like|
|-|-|
|**Poor name**|A name that doesn't tell you what the thing *means*: `t`, `p`, `move()`|
|**Magic number**|A literal number whose meaning you have to work out: `7`, `5`, `4`|
|**Duplicated code**|The same idea written out more than once|
|**Long or tangled method**|A method doing several jobs at once|
|**Primitive obsession**|Using an `int` or `char` for something that deserves its own type|

📝 **Write down every smell you find**, with a line number, in a list like this:

```
line 38  Duplicated code: the X check and the O check are identical apart from the letter
line 11  Magic number: what does 5 mean?
...
```

Keep the list. At the end of the lab you will tick off which change fixed each smell.

\---

## 2\. Easy changes 🔧

Do these **one at a time**. After **each** one:

> ✅ Run the tests. Green? \*\*Commit.\*\* Red? \*\*Undo\*\* and try again more carefully.

In Visual Studio, put the cursor on a name and press **Ctrl+R, Ctrl+R** to rename it everywhere it's used, including in `test.cpp`. Renaming by hand is how bugs creep in.

- [ ] **2.1** `move()` doesn't say what it does. Rename it to `bestMoveFor()`.
- [ ] **2.2** In `play()`, rename the parameters `c` → `column` and `p` → `player`. Do the same for `p` in `bestMoveFor()`.
- [ ] **2.3** In `bestMoveFor()`, the loop variable `i` isn't just a counter: it's a **column** the player might drop a piece into. Rename it to `column` (in both loops).
- [ ] **2.4** In `play()`, rename `r` → `row` and `b` → `newBoard`.
- [ ] **2.5** `-1` is a flag meaning "there is no move". Add a constant to the class and use it in place of the `-1`. In `test.cpp`, change the `-1` in `FullBoardHasNoMove` to `ConnectFour::NoMove`.

```cpp
  static const int NoMove = -1;
  ```


- [ ] **2.6** `'-'` means "empty cell". Add a constant for `Empty` and use it everywhere `'-'` is used in `ConnectFour.cpp`.
- [ ] **2.7** The expression `r \* 7 + c` (row × width + column) appears **many** times. Extract it into a private method:

```cpp
  int indexOf(int row, int column) const;
  ```

  and use it in `play()` and `winner()`.

- [ ] **2.8** In `bestMoveFor()`, `board\[column] == Empty` checks only *one* cell, yet it is really asking a question about the whole column. 🤔 **Which cell is it checking, and why is that enough?** Extract it into a private method with a name that says what it *means*:

  ```cpp
  bool canPlayIn(int column) const;
  ```

  Use it in **both** loops.

- [ ] **2.9** What does the object `t` represent? Give it a name that says so. (Hint: it's the game *after* something has happened.)

  > 📌 \*\*Checkpoint 1.\*\* Compare your code with a neighbour's. Are your names the same? Does it matter if they're different?

  \---

  ## 3\. Fuse the loops 🔧 then 🏗️

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

  > 💡 \*\*When is it safe to fuse two loops?\*\* When they loop over the same range, and \*\*neither\*\* loop exits early or depends on something the other loop works out.

  So first remove the early exits, one loop at a time. **Tests must stay green after every step.**

  ### Step 3.1 🔧: loop 2 records its answer instead of returning it

```cpp
    int defaultMove = NoMove;
    for (int column = 0; column < 7; column++) {
        if (canPlayIn(column) \&\& defaultMove == NoMove)
            defaultMove = column;
    }
    return defaultMove;
```

  The `defaultMove == NoMove` check keeps the **first** playable column, exactly as the old `return` did. Run the tests: green? Commit.

  ### Step 3.2 🔧: loop 1 does the same

```cpp
    int winningMove = NoMove;
    for (int column = 0; column < 7; column++) {
        if (canPlayIn(column) \&\& winningMove == NoMove) {
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

  ### Step 3.3 : fuse

  The two loops now have the same header and no early exits, so it's safe. Move the body of loop 2 into loop 1 and delete loop 2. Run the tests: green? Commit.

  ### Step 3.4 : change of hat. Simplify the default move

  The rules only say *"if you can't win, play **any** legal move"*. We don't care **which** one. So the `defaultMove == NoMove` guard is doing work nobody asked for. **Delete it** (keep `canPlayIn(column)`).

  This **changes behaviour**: `defaultMove` is now the *last* playable column instead of the first. Run the tests.

  > ⚠️ \*\*Two tests are expected to go red here:\*\* `ChooseMoveTest.NoWinPicksFirstOpenColumn` and `ChooseMoveTest.SkipsFullColumn`. \*\*Don't undo.\*\*
>
> 🤔 The code still obeys the rules, so why are the tests failing? The tests check for \*\*one particular\*\* legal move when the rules allow \*\*any\*\* legal move. That's an \*\*over-specified\*\* test: it locks in a detail nobody cares about, and blocks a perfectly good change.
>
> \*\*Fix the tests, not the code.\*\* Rename `NoWinPicksFirstOpenColumn` to `NoWinPicksAValidColumn` and check the move is a real column, using `EXPECT\_GE(move, 0)` and `EXPECT\_LT(move, 7)` in place of `EXPECT\_EQ`. In `SkipsFullColumn`, check the move is \*\*not\*\* column 0 (`EXPECT\_NE`) and is a real column.

  Green again? Commit.

  ### Step 3.5 : one variable, one exit

  You now have two variables and some `if`s to choose between them. Simplify to a **single** `result` variable:

* If a column is not playable, skip it (`continue`).
* If playing the column wins, you can `return column;` straight away. Nothing beats a win, so stopping early is fine.
* Otherwise, remember it: `result = column;`.
* After the loop, `return result;`.

  The whole method should now fit in about 10 lines. Run the tests: green? Commit.

  > 📌 \*\*Checkpoint 2.\*\*

  \---

  ## 4\. Magic numbers and duplication 🔧

  Look back at your smell list. 🤔 **Which part of the code smells worst now?**

  It is probably `winner()`. It's full of magic numbers, and the `'X'` check and the `'O'` check are copies of each other.

  ### Step 4.1: name the numbers

  Add these to the class:

```cpp
static constexpr int Rows = 6;
static constexpr int Columns = 7;
static constexpr int WinLength = 4;
```

  Replace the magic numbers **one kind at a time**, running the tests in between:

* every `7` → `Columns`
* the `6` in `winner()` → `Rows`
* the `5` in `play()` → ?  (*It's the bottom row. How do you write that using `Rows`?*)

  Then look at `c < 4` in `winner()`.

  > \*\*Careful!\*\* Is that `4` the same thing as `WinLength`? Try it with a bigger board: on a 10-column board, what should the limit be? It's actually `Columns - WinLength + 1`, which just \*happens\* to equal 4 here. One literal hiding two different meanings is exactly why magic numbers are dangerous.

  ### Step 4.2: remove the X/O duplication

  Add a helper that reads a cell:

```cpp
char cellAt(int row, int column) const;   // returns board\[indexOf(row, column)]
```

  Then, instead of checking for `'X'` and then for `'O'`, read the **first** cell of the four. If it's not `Empty`, check that the other three **match it**:

  ```cpp
char first = cellAt(row, column);
if (first != Empty \&\& cellAt(row, column + 1) == first \&\& /\* ... \*/)
    return first;
```

  Half of `winner()` disappears. Run the tests: green? Commit.

  ### Step 4.3: turn "four in a row" into a loop

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

  > 🛡️ The test `WinnerTest.LineDoesNotWrapAroundTheEdge` protects you here. In the string, the last cell of one row sits right next to the first cell of the next. Forget the bounds check and that test goes red.

  Run the tests: green? Commit.

  > 📌 \*\*Checkpoint 3a.\*\*

  \---

  ## 5\. More ways to win 🏗️

  We're still not playing real Connect Four: you can also win **vertically** and on **both diagonals**.

  ### Step 5.1: tests first

  Write these four tests in the `WinnerTest` group. Use the `rows(...)` helper so you can *see* each board. **Run them and watch them fail** (all except the last one, which should already pass. Why?)

|Test|Board idea|Expect|
|-|-|-|
|`VerticalFourIsAWin`|four `X` stacked in one column|`'X'`|
|`DiagonalUpRightIsAWin`|four `X` climbing `/` from bottom-left|`'X'`|
|`DiagonalUpLeftIsAWin`|four `O` climbing `\\` from bottom-right|`'O'`|
|`DiagonalDoesNotWrapAroundTheEdge`|`X` at (row 0, col 6), (2,0), (3,1), (4,2)|`'-'`|

> 🤔 For the last test, work out the string positions of those four cells. What do you notice? What would a "lazy" diagonal check get wrong?

### Step 5.2: make them pass

If section 4 went well, this should be a **small** change. A line can run in four directions:

```cpp
const int Directions\[]\[2] = {
    {0, 1},    // horizontal: step right
    {1, 0},    // vertical: step down
    {1, 1},    // diagonal: step down and right
    {1, -1},   // diagonal: step down and left
};
```

In `winner()`, loop over these directions and call `lineOwner()` for each. Run the tests: green? Commit.

> 🤔 \*\*Reflect:\*\* How many lines did you have to change to add three new ways to win? How many would it have taken in the original code?
>
> 🤔 Your teacher now wants \*\*Connect Five\*\* on a \*\*9 × 7\*\* board. What would you change?

> 📌 \*\*Checkpoint 3b.\*\*

\---

## 6\. A smarter player: Stretch ⭐

So far, the player wins if it can and otherwise plays any legal move. It doesn't even notice when the opponent is about to win.

We'll give every move a **score**, and pick the move with the highest score. There is **one** scoring rule for this whole section:

|Score|Meaning|
|-|-|
|**100**|The move **wins** the game|
|**0**|The move lets the **opponent win** on their very next turn|
|**50**|Anything else|

Once moves have scores, a move is no longer just a column number. It is a column **and** a score. An `int` can't hold both: that's *primitive obsession*. Time for a class.

### Step 6.1 🔧: a `Move` class, with tests

Put this class in `ConnectFour.h`, above `ConnectFour`. Write tests for `isBetterThan()` **first**, in a new `MoveTest` group (use `EXPECT\_TRUE` and `EXPECT\_FALSE`): a higher score is better, an equal score is **not** better, and any real move is better than `Move::none()`.

```cpp
class Move {
public:
    Move(int column, int score);
    int column() const;
    int score() const;
    bool isBetterThan(const Move\& other) const;
    static Move none();      // column = -1, score = -1: worse than any real move
private:
    int column\_;
    int score\_;
};
```

`Move` is a **value object**: it has getters but no setters, and once created it never changes.

### Step 6.2 🔧: use `Move` inside `bestMoveFor()`

Add a public method `int scoreMove(int column, char player) const`. For now it returns **100** if the move wins and **50** otherwise.

Rewrite `bestMoveFor()` as "find the best `Move`", the same pattern as finding the largest number in a list:

```cpp
Move best = Move::none();
// for each playable column:
//     Move candidate(column, scoreMove(column, player));
//     if (candidate.isBetterThan(best)) best = candidate;
return best.column();
```

> 💡 `bestMoveFor()` \*\*still returns an `int`\*\*, so none of the existing tests need to change. `Move` is an internal detail. Callers don't need to know it exists.

Run the tests: green? Commit.

### Step 6.3 🏗️: don't hand the opponent a win

Write these tests **first** and watch them fail:

Put these in a new `ScoringTest` group.

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

   Now make them pass. You will probably want:

* `char opponentOf(char player)`: `'X'` ↔ `'O'`
* `bool canWinNextTurn(char player) const`: is there **any** playable column where this player wins straight away?

  In `scoreMove()`: play the move, then ask whether the **opponent** can win next turn on the resulting board.

  > 🤔 You never wrote a rule that says "block the opponent". So why does `BlocksOpponentWin` pass? (Look at what every \*other\* column scores.)

  > 📌 \*\*Checkpoint 4.\*\*

  ### Further stretch (pick any)

* **Prefer the centre.** Pieces in the middle columns take part in more possible lines. Among moves with equal scores, prefer the column nearest the centre. Can you do it by changing `scoreMove()` only? Which tests do you need to write first?
* **Double threats.** A move that leaves you **two** different winning columns can't be blocked. Score it 90.

  \---

  ## Wrap-up

  Go back to your smell list from section 1. Next to each smell, write the step that removed it. Are any smells left?

  \---

  # Submission

1. **One person in the pair** pushes the project to the GitHub repo.
3. **Each person** answers **four** of the following questions in the Blackboard submission:

   1. **Collaboration:** What did you learn about working together with your partner? Were there any challenges you faced?
   2. **Communication:** How did you communicate your ideas to each other? What strategies were effective?
   3. **Role distribution:** How did you decide who would take on which roles or tasks during the activity? Was this effective?
   4. **Learning outcomes:** What new skills or concepts did you learn from your partner? Did their perspective change your understanding of the material?
   5. **Feedback:** How did you give and receive feedback during the pairing? Was there anything you found particularly helpful or unhelpful?
   6. **Time management:** How did you manage your time together? Were there any time-related challenges?
   7. **Personal growth:** What did you discover about your own learning style or preferences through this pairing experience?
   8. **Future improvements:** If you could do this pairing activity again, what would you change to make it more effective?

