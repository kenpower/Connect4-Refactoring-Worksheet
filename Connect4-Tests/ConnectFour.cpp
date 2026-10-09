#include "pch.h"
#include "ConnectFour.h"

ConnectFour::ConnectFour(const std::string& s) : board(s) {}

std::string ConnectFour::getBoard() const {
    return board;
}

ConnectFour ConnectFour::play(int c, char p) const {
    std::string b = board;
    for (int r = 5; r >= 0; r--) {
        if (b[r * 7 + c] == '-') {
            b[r * 7 + c] = p;
            break;
        }
    }
    return ConnectFour(b);
}

int ConnectFour::move(char p) const {
    for (int i = 0; i < 7; i++) {
        if (board[i] == '-') {
            ConnectFour t = play(i, p);
            if (t.winner() == p)
                return i;
        }
    }
    for (int i = 0; i < 7; i++) {
        if (board[i] == '-')
            return i;
    }
    return -1;
}

char ConnectFour::winner() const {
    for (int r = 0; r < 6; r++) {
        for (int c = 0; c < 4; c++) {
            if (board[r * 7 + c] == 'X' && board[r * 7 + c + 1] == 'X' &&
                board[r * 7 + c + 2] == 'X' && board[r * 7 + c + 3] == 'X')
                return 'X';
            if (board[r * 7 + c] == 'O' && board[r * 7 + c + 1] == 'O' &&
                board[r * 7 + c + 2] == 'O' && board[r * 7 + c + 3] == 'O')
                return 'O';
        }
    }
    return '-';
}
