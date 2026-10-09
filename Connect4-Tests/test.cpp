#include "pch.h"
// Tests for ConnectFour, using GoogleTest.
// Build and run: see the "Setup" section of LAB.md.
#include "ConnectFour.h"
#include <gtest/gtest.h>
#include <string>

// Builds a 42-character board from six rows, TOP row first.
// Writing boards this way lets you "see" them in the test.
static std::string rows(
    const std::string& r0, 
    const std::string& r1,
    const std::string& r2, 
    const std::string& r3,
    const std::string& r4, 
    const std::string& r5) {
        return r0 + r1 + r2 + r3 + r4 + r5;
}

static std::string emptyBoard() {
    return rows("-------",
        "-------",
        "-------",
        "-------",
        "-------",
        "-------");
}

// ---------- play ----------

TEST(PlayTest, DropsPieceToBottomRow) {
    ConnectFour game(emptyBoard());
    ConnectFour after = game.play(3, 'X');
    EXPECT_EQ(after.getBoard(), 
        rows("-------",
        "-------",
        "-------",
        "-------",
        "-------",
        "---X---"));
}

TEST(PlayTest, StacksOnTopOfExistingPiece) {
    ConnectFour game(rows("-------",
        "-------",
        "-------",
        "-------",
        "-------",
        "---X---"));
    ConnectFour after = game.play(3, 'O');
    EXPECT_EQ(after.getBoard(), rows("-------",
        "-------",
        "-------",
        "-------",
        "---O---",
        "---X---"));
}

TEST(PlayTest, DoesNotChangeOriginalGame) {
    ConnectFour game(emptyBoard());
    game.play(3, 'X');
    EXPECT_EQ(game.getBoard(), emptyBoard());
}

// ---------- winner ----------

TEST(WinnerTest, EmptyBoardHasNoWinner) {
    ConnectFour game(emptyBoard());
    EXPECT_EQ(game.winner(), '-');
}

TEST(WinnerTest, HorizontalFourIsAWinForX) {
    ConnectFour game(rows("-------",
        "-------",
        "-------",
        "-------",
        "OOO----",
        "XXXX---"));
    EXPECT_EQ(game.winner(), 'X');
}

TEST(WinnerTest, HorizontalFourIsAWinForO) {
    ConnectFour game(rows("-------",
        "-------",
        "-------",
        "-------",
        "X-X----",
        "X-XOOOO"));
    EXPECT_EQ(game.winner(), 'O');
}

TEST(WinnerTest, ThreeInARowIsNotAWin) {
    ConnectFour game(rows("-------",
        "-------",
        "-------",
        "-------",
        "OO-----",
        "XXX----"));
    EXPECT_EQ(game.winner(), '-');
}

TEST(WinnerTest, FourWithAGapIsNotAWin) {
    ConnectFour game(rows("-------",
        "-------",
        "-------",
        "-------",
        "OOOO---",   // O's are floating - fine for this test
        "XX-XX--"));
    EXPECT_NE(game.winner(), 'X');
}

TEST(WinnerTest, LineDoesNotWrapAroundTheEdge) {
    // In the 42-character string, the end of one row sits right next to the
    // start of the next. These four X's are adjacent in the string, but not on the board.
    ConnectFour game(rows("-------",
        "-------",
        "-------",
        "-------",
        "-----XX",
        "XXOO-OO"));
    EXPECT_EQ(game.winner(), '-');
}

// ---------- choosing a move ----------

TEST(ChooseMoveTest, TakesWinningColumn) {
    ConnectFour game(rows("-------",
        "-------",
        "-------",
        "-------",
        "O------",
        "OXXX--O"));
    EXPECT_EQ(game.move('X'), 4);
}

TEST(ChooseMoveTest, FindsWinForO) {
    ConnectFour game(rows("-------",
        "-------",
        "-------",
        "-------",
        "X------",
        "XX-OOOX"));
    EXPECT_EQ(game.move('O'), 2);
}

TEST(ChooseMoveTest, NoWinPicksFirstOpenColumn) {
    ConnectFour game(emptyBoard());
    EXPECT_EQ(game.move('X'), 0);
}

TEST(ChooseMoveTest, SkipsFullColumn) {
    ConnectFour game(rows("X------",
        "O------",
        "X------",
        "O------",
        "X------",
        "O------"));
    EXPECT_EQ(game.move('X'), 1);
}

TEST(ChooseMoveTest, FullBoardHasNoMove) {
    ConnectFour game(rows("XXOOXXO",
        "OOXXOOX",
        "XXOOXXO",
        "OOXXOOX",
        "XXOOXXO",
        "OOXXOOX"));
    EXPECT_EQ(game.move('X'), -1);
}
