#pragma once
#include <string>

// A Connect Four position.
// The board is a string of 42 characters: 6 rows of 7, TOP row first.
// '-' is an empty cell, 'X' and 'O' are the players' pieces.
class ConnectFour {
public:
    ConnectFour(const std::string& s);

    ConnectFour play(int c, char p) const;
    int move(char p) const;
    char winner() const;

    std::string getBoard() const;

private:
    static const int x = 1;
    std::string board;
};
