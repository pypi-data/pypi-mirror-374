# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES.
#                         All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# IMPORTANT:
#   * install_info.py is a generated file and should not be modified by hand
from __future__ import annotations

def get_libpath(lib_base_name: str, full_lib_name: str) -> str:
    from os.path import join, exists, dirname
    import sys
    import platform

    lg_path = dirname(dirname(__file__))
    so_ext = {
        "": "",
        "Java": ".jar",
        "Linux": ".so",
        "Darwin": ".dylib",
        "Windows": ".dll"
    }[platform.system()]

    def find_liblegate(libdir):
        if not libdir:
            return None

        def lib_exists(path: str) -> bool:
            return exists(join(libdir, path))

        for name in (
            full_lib_name,
            f"{lib_base_name}{so_ext}",
            f"liblegate{so_ext}",
        ):
            if lib_exists(name):
                return str(libdir)
        return None

    from .util.fs import get_legate_paths

    return (
        find_liblegate(get_legate_paths().legate_lib_path) or
        find_liblegate(join(dirname(dirname(dirname(lg_path))), "lib")) or
        find_liblegate(join(dirname(dirname(sys.executable)), "lib")) or
        ""
    )


LEGATE_ARCH: str = "legate-all"

libpath: str = get_libpath("liblegate", "liblegate.so.25.08.00")

# wrap in str to placate pyright
networks: list[str] = str("ucx").split()

max_dim: int = int("6")

max_fields: int = int("256")

conduit: str = ""

build_type: str = "Release"

# this is to support simpler templating on the cmake side
ON, OFF = True, False

use_cuda: bool = ON

use_openmp: bool = OFF

legion_version: str = "25.8.0"

legion_git_branch: str = "16441d05a66bdf0f21e271b943a60315f113a55e"

legion_git_repo: str = "https://gitlab.com/StanfordLegion/legion.git"

wheel_build: bool = ON

configure_options: str = ""
