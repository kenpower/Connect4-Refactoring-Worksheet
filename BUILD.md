# Building and running the tests

The project is built with **CMake**. The same `CMakeLists.txt` works in Visual Studio, CLion and VS Code, and from the command line, on Windows and Linux. There is no `.sln` file: you open the **folder**.

GoogleTest is **downloaded automatically** the first time CMake configures the project. That first configure needs an internet connection and takes a minute or so while GoogleTest builds. After that it's fast.

When it works, you should see **14 tests, all passing**.

> **Using RedGreenGo?** The game only sees test runs that go through **CTest**: Visual Studio's Test Explorer, VS Code's Testing view, CLion's **All CTest** configuration, or `ctest` on the command line. Always **run all the tests** that way. Running the test program directly (CLion's green ▶ in the gutter, or `./build/connect4_tests`) works, but the game won't see the results.

Pick the section for your setup:

- [Visual Studio 2022 or later (Windows)](#visual-studio-2022-or-later-windows)
- [CLion (Windows or Linux)](#clion-windows-or-linux)
- [VS Code (Windows or Linux)](#vs-code-windows-or-linux)
- [Command line (Linux)](#command-line-linux)
- [Command line (Windows)](#command-line-windows)
- [Troubleshooting](#troubleshooting)

---

## Visual Studio 2022 or later (Windows)

**You need:** Visual Studio 2022 or later with the **Desktop development with C++** workload. Make sure the **C++ CMake tools for Windows** component is ticked (it is by default). Check in *Visual Studio Installer → Modify*.

1. **File → Open → Folder…** and choose the repo folder (the one containing `CMakeLists.txt`). Don't look for a `.sln`; there isn't one.
2. Wait for the Output window (*Show output from: CMake*) to say **CMake generation finished**. The first time, this includes downloading GoogleTest.
3. **Build → Build All** (Ctrl+Shift+B).
4. **Test → Test Explorer**, then **Run All Tests**.

Rename a symbol: **Ctrl+R, Ctrl+R**.

> If Test Explorer is empty, build once and then click **Run All** again: the tests are discovered from the built executable.

---

## CLion (Windows or Linux)

**You need:** CLion. It comes with CMake and, on Windows, a MinGW compiler, so nothing else is required. On Windows you can also use the Visual Studio compiler if you have it installed (*Settings → Build, Execution, Deployment → Toolchains*).

1. **File → Open…** and choose the repo folder.
2. If CLion asks for a CMake profile, accept the default **Debug** profile.
3. Wait for the CMake tool window to finish loading.
4. In the run configuration list (top-right), choose **All CTest** and click ▶ to run all the tests. Results appear in the **Run** window as a test tree. CLion creates **All CTest** by itself once CMake has loaded; if it isn't in the list, use *Run → Edit Configurations → + → CTest Application*.

   > Don't use the green ▶ in the gutter next to a `TEST(...)`, or the **connect4_tests** configuration. They run the tests too, but not through CTest, so RedGreenGo can't see the results.

Rename a symbol: **Shift+F6**.

> CLion builds into `cmake-build-debug/`. It's ignored by git.

---

## VS Code (Windows or Linux)

**You need:**

- These extensions: **C/C++** (Microsoft) and **CMake Tools** (Microsoft). The *C/C++ Extension Pack* includes both.
- CMake and a C++ compiler:
  - **Linux:** `sudo apt install build-essential cmake` (Debian/Ubuntu) or `sudo dnf install gcc-c++ cmake` (Fedora).
  - **Windows:** install **Build Tools for Visual Studio 2022** (or full Visual Studio) with the *Desktop development with C++* workload. This gives you both the compiler and CMake.

Steps:

1. **File → Open Folder…** and choose the repo folder.
2. CMake Tools asks you to **select a kit** (a compiler). Pick:
   - Linux: **GCC** (or Clang).
   - Windows: **Visual Studio Build Tools 2022 Release – amd64** (or similar). If none is listed, run *CMake: Scan for Kits* from the Command Palette (Ctrl+Shift+P).
3. Wait for CMake to configure (the Output panel shows *CMake/Build*).
4. Click **Build** in the status bar, or run *CMake: Build* (F7).
5. Open the **Testing** view (the flask icon in the left bar) and click **Run Tests**. You can also run *CMake: Run Tests* from the Command Palette.

Rename a symbol: **F2**.

> If the Testing view says **no tests found**, CMake probably hasn't configured yet. Check the status bar: if it says **No Kit Selected**, click it (or run *CMake: Select a Kit*) and choose your compiler. Then build (F7) and click the refresh icon at the top of the Testing view.

---

## Command line (Linux)

**You need:** a C++17 compiler and CMake 3.20 or newer.

```bash
sudo apt install build-essential cmake      # Debian/Ubuntu; once only
```

From the repo folder:

```bash
cmake -S . -B build                          # configure (downloads GoogleTest the first time)
cmake --build build                          # compile
ctest --test-dir build --output-on-failure   # run the tests
```

After you change code, only the last two commands are needed. For GoogleTest's own colourful output, run the executable directly (RedGreenGo won't see this run, so run `ctest` too):

```bash
./build/connect4_tests
```

---

## Command line (Windows)

Open **Developer PowerShell for VS 2022** (from the Start menu), so the compiler and CMake are on your `PATH`. Then from the repo folder:

```powershell
cmake -S . -B build
cmake --build build
ctest --test-dir build -C Debug --output-on-failure
```

Run the executable directly with `.\build\Debug\connect4_tests.exe` (RedGreenGo won't see that run, so run `ctest` too).

---

## Troubleshooting

**Configure fails while downloading GoogleTest.** CMake needs to reach `github.com` the first time. Check your internet connection or proxy, then delete the build folder and configure again.

**Strange errors after switching compiler or IDE.** Each IDE uses its own build folder (`out/` for Visual Studio, `cmake-build-*/` for CLion, `build/` for VS Code and the command line). If one gets confused, close the IDE, delete that folder, and reopen. All of these folders are ignored by git.

**`CMake 3.20 or higher is required`.** Your CMake is too old. On older Linux distributions, install a newer one with `pip install --user cmake` or from [cmake.org](https://cmake.org/download/).

**The tests compile but Test Explorer / the Testing view shows nothing.** Build first: tests are discovered by running the built executable. Then refresh the test view.

**Linker errors mentioning `NoMove`, `Empty`, `Columns` etc.** Declare the constants as `static constexpr`, not `static const` (see step 2.3 in the README).
