import os
import ycm_core
import subprocess
import glob

cxxflags = [
    "-Weverything",
    "-Wno-c++98-compat",
    "-Wno-c++98-compat-pedantic",
    "-Wno-covered-switch-default",
    "-Wno-padded",
    "-Wno-weak-vtables",
    "-Wno-exit-time-destructors",
    "-Wno-global-constructors",
    # You 100% do NOT need -DUSE_CLANG_COMPLETER in your flags; only the YCM
    # source code needs it.
    "-DUSE_CLANG_COMPLETER",
    "-std=c++20",
    "-x",
    "c++",
    "-stdlib=libc++",
    "-Isrc/include/",
    "-Itest/common/include/",
    "-DDGALE_RUN_CLANG_TIDY",
]

cflags = [
    "-Wextra",
    "-Wall",
    # You 100% do NOT need -DUSE_CLANG_COMPLETER in your flags; only the YCM
    # source code needs it.
    "-DUSE_CLANG_COMPLETER",
    "-std=c11",
    "-x",
    "c",
    "-Isrc/include/",
    "-Itest/common/include/",
]

def MakeRelativePathsInFlagsAbsolute(flags, working_directory):
    if not working_directory:
        return list(flags)
    new_flags = []
    make_next_absolute = False
    path_flags = ["-isystem", "-I", "-iquote", "--sysroot="]
    for flag in flags:
        new_flag = flag

        if make_next_absolute:
            make_next_absolute = False
            if not flag.startswith("/"):
                new_flag = os.path.join(working_directory, flag)

        for path_flag in path_flags:
            if flag == path_flag:
                make_next_absolute = True
                break

            if flag.startswith(path_flag):
                path = flag[len(path_flag) :]
                new_flag = path_flag + os.path.join(working_directory, path)
                break

        if new_flag:
            new_flags.append(new_flag)
    return new_flags


def Settings(filename, **kwargs):
    relative_to = os.path.dirname(os.path.abspath(__file__))
    extension = os.path.splitext(filename)[1]
    flags = []
    print(extension)
    if extension == ".c" or extension == ".h":
        flags = cflags
    else:
        flags = cxxflags
    final_flags = MakeRelativePathsInFlagsAbsolute(flags, relative_to)
    return {"flags": final_flags}
