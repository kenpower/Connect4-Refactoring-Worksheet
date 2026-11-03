# Smell log

**Pair:** _name_ & _name_

## Suggested Smells (not all will apply to this project)
- Mysterious Name : a function/variable's name is vague or misleading
- Magic Numbers : unexplained literal values scattered through the code
- Long Function : one function does too many things
- Duplicated Code : several loops repeat the same iteration
- Deeply Nested Conditionals : layers of nested ifs hide the main path
- Primitive Obsession : raw strings or numbers stand in for domain ideas like money or phone numbers
- Comments : comments used to explain code that should be clearer on its own
- Data Clumps : the same group of values keeps showing up together
- Long Parameter List : a function takes too many arguments

Record each smell **before** you change any code, with its line number in `ConnectFour.cpp`. Add as many rows as you need. At the end of the lab, fill in **Fixed in** with the step that removed it (e.g. `2.3`), or `still there`.

The first two rows are examples.

|Line(s)|Smell|What's wrong|Fixed in|
|-|-|-|-|
|23|Poor name|`t` doesn't say what it is; it's the game *after* a move is played||
|38–43|Duplicated code|The X check and the O check are identical apart from the letter||
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
