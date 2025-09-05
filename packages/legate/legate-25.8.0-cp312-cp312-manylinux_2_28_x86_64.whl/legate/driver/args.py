# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES.
#                         All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from argparse import REMAINDER, ArgumentDefaultsHelpFormatter, ArgumentParser
from os import getenv
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..util.types import RunMode

from .. import __version__
from ..util import defaults
from ..util.args import InfoAction
from ..util.shared_args import (
    AUTO_CONFIG,
    CONSENSUS,
    CPUS,
    DISABLE_MPI,
    FBMEM,
    FIELD_REUSE_FRACTION,
    FIELD_REUSE_FREQUENCY,
    GPUS,
    INLINE_TASK_LAUNCH,
    IO_USE_VFD_GDS,
    LAUNCHER,
    LAUNCHER_EXTRA,
    MAX_EXCEPTION_SIZE,
    MIN_CPU_CHUNK,
    MIN_GPU_CHUNK,
    MIN_OMP_CHUNK,
    NODES,
    NUMAMEM,
    OMPS,
    OMPTHREADS,
    RANKS_PER_NODE,
    REGMEM,
    SHOW_CONFIG,
    SHOW_MEMORY_USAGE,
    SHOW_PROGRESS,
    SYSMEM,
    UTILITY,
    WARMUP_NCCL,
    WINDOW_SIZE,
    ZCMEM,
)

__all__ = ("parser",)

RUN_MODE_OPTIONS: tuple[RunMode, ...] = ("python", "exec")


def _get_ompi_config() -> tuple[int, int] | None:
    if not (ranks_env := getenv("OMPI_COMM_WORLD_SIZE")):
        return None

    if not (ranks_per_node_env := getenv("OMPI_COMM_WORLD_LOCAL_SIZE")):
        return None

    try:
        ranks, ranks_per_node = int(ranks_env), int(ranks_per_node_env)
    except ValueError:
        msg = (
            "Expected OMPI_COMM_WORLD_SIZE and OMPI_COMM_WORLD_LOCAL_SIZE to "
            f"be integers, got OMPI_COMM_WORLD_SIZE={ranks_env} and "
            f"OMPI_COMM_WORLD_LOCAL_SIZE={ranks_per_node_env}"
        )
        raise ValueError(msg)

    if ranks % ranks_per_node != 0:
        msg = (
            "Detected incompatible ranks and ranks-per-node from "
            f"OMPI_COMM_WORLD_SIZE={ranks} and "
            f"OMPI_COMM_WORLD_LOCAL_SIZE={ranks_per_node}"
        )
        raise ValueError(msg)

    return ranks // ranks_per_node, ranks_per_node


def _get_mv2_config() -> tuple[int, int] | None:
    if not (ranks_env := getenv("MV2_COMM_WORLD_SIZE")):
        return None

    if not (ranks_per_node_env := getenv("MV2_COMM_WORLD_LOCAL_SIZE")):
        return None

    try:
        ranks, ranks_per_node = int(ranks_env), int(ranks_per_node_env)
    except ValueError:
        msg = (
            "Expected MV2_COMM_WORLD_SIZE and MV2_COMM_WORLD_LOCAL_SIZE to "
            f"be integers, got MV2_COMM_WORLD_SIZE={ranks_env} and "
            f"MV2_COMM_WORLD_LOCAL_SIZE={ranks_per_node_env}"
        )
        raise ValueError(msg)

    if ranks % ranks_per_node != 0:
        msg = (
            "Detected incompatible ranks and ranks-per-node from "
            f"MV2_COMM_WORLD_SIZE={ranks} and "
            f"MV2_COMM_WORLD_LOCAL_SIZE={ranks_per_node}"
        )
        raise ValueError(msg)

    return ranks // ranks_per_node, ranks_per_node


_SLURM_CONFIG_ERROR = (
    "Expected SLURM_TASKS_PER_NODE to be a single integer ranks per node, or "
    "of the form 'A(xB)' where A is an integer ranks per node, and B is an "
    "integer number of nodes, got SLURM_TASKS_PER_NODE={value}"
)


def _get_slurm_config() -> tuple[int, int] | None:  # noqa: C901, PLR0911
    if not (nodes_env := getenv("SLURM_JOB_NUM_NODES")):
        return None

    nprocs_env = getenv("SLURM_NPROCS")
    ntasks_env = getenv("SLURM_NTASKS")
    tasks_per_node_env = getenv("SLURM_TASKS_PER_NODE")

    # at least one of these needs to be set
    if not any((nprocs_env, ntasks_env, tasks_per_node_env)):
        return None

    # use SLURM_TASKS_PER_NODE if it is given
    if tasks_per_node_env is not None:
        try:
            return 1, int(tasks_per_node_env)
        except ValueError:
            m = re.match(r"^(\d*)\(x(\d*)\)$", tasks_per_node_env.strip())
            if m:
                try:
                    return int(m.group(2)), int(m.group(1))
                except ValueError:
                    pass
            raise ValueError(
                _SLURM_CONFIG_ERROR.format(value=tasks_per_node_env)
            )

    # prefer newer SLURM_NTASKS over SLURM_NPROCS
    if ntasks_env is not None:
        try:
            nodes, ranks = int(nodes_env), int(ntasks_env)
        except ValueError:
            msg = (
                "Expected SLURM_JOB_NUM_NODES and SLURM_NTASKS to "
                f"be integers, got SLURM_JOB_NUM_NODES={nodes_env} and "
                f"SLURM_NTASKS={ntasks_env}"
            )
            raise ValueError(msg)

        if ranks % nodes != 0:
            msg = (
                "Detected incompatible ranks and ranks-per-node from "
                f"SLURM_JOB_NUM_NODES={nodes} and "
                f"SLURM_NTASKS={ranks}"
            )
            raise ValueError(msg)

        return nodes, ranks // nodes

    # fall back to older SLURM_NPROCS
    if nprocs_env is not None:
        try:
            nodes, ranks = int(nodes_env), int(nprocs_env)
        except ValueError:
            msg = (
                "Expected SLURM_JOB_NUM_NODES and SLURM_NPROCS to "
                f"be integers, got SLURM_JOB_NUM_NODES={nodes_env} and "
                f"SLURM_NPROCS={nprocs_env}"
            )
            raise ValueError(msg)

        if ranks % nodes != 0:
            msg = (
                "Detected incompatible ranks and ranks-per-node from "
                f"SLURM_JOB_NUM_NODES={nodes} and "
                f"SLURM_NPROCS={ranks}"
            )
            raise ValueError(msg)

        return nodes, ranks // nodes

    return None


def detect_multi_node_defaults() -> tuple[dict[str, Any], dict[str, Any]]:
    nodes_kw = dict(NODES.kwargs)
    ranks_per_node_kw = dict(RANKS_PER_NODE.kwargs)
    where = None

    if config := _get_ompi_config():
        where = "OMPI"
    elif config := _get_mv2_config():
        where = "MV2"
    elif config := _get_slurm_config():
        where = "SLURM"
    else:
        config = defaults.LEGATE_NODES, defaults.LEGATE_RANKS_PER_NODE
        where = None

    nodes, ranks_per_node = config
    nodes_kw["default"] = nodes
    ranks_per_node_kw["default"] = ranks_per_node

    if where:
        extra = f" [default auto-detected from {where}]"
        nodes_kw["help"] += extra
        ranks_per_node_kw["help"] += extra

    return nodes_kw, ranks_per_node_kw


parser = ArgumentParser(
    description="Legate Driver",
    allow_abbrev=False,
    formatter_class=ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "command",
    nargs=REMAINDER,
    help="A python script to run, plus any arguments for the script. "
    "Any arguments after the script will be passed to the script, i.e. "
    "NOT used as arguments to legate itself.",
)

parser.add_argument(
    "--run-mode",
    default=None,
    choices=RUN_MODE_OPTIONS,
    help="Whether to run the command using the python interpreter, or "
    "as a bare executable. By default, commands that end in .py will be run "
    "as a python script, and those that don't will be run as an executable. "
    "If --module is specified, python mode will also be assumed by default. "
    "[legate-only, not supported with standard Python invocation]",
)

parser.add_argument(AUTO_CONFIG.name, **AUTO_CONFIG.kwargs)
parser.add_argument(SHOW_CONFIG.name, **SHOW_CONFIG.kwargs)
parser.add_argument(SHOW_MEMORY_USAGE.name, **SHOW_MEMORY_USAGE.kwargs)
parser.add_argument(SHOW_PROGRESS.name, **SHOW_PROGRESS.kwargs)

nodes_kw, ranks_per_node_kw = detect_multi_node_defaults()

multi_node = parser.add_argument_group("Multi-node configuration")
multi_node.add_argument(NODES.name, **nodes_kw)
multi_node.add_argument(RANKS_PER_NODE.name, **ranks_per_node_kw)
multi_node.add_argument(LAUNCHER.name, **LAUNCHER.kwargs)
multi_node.add_argument(LAUNCHER_EXTRA.name, **LAUNCHER_EXTRA.kwargs)


binding = parser.add_argument_group("Hardware binding")


binding.add_argument(
    "--cpu-bind",
    help="CPU cores to bind each rank to. Comma-separated core IDs as "
    "well as ranges are accepted, as reported by `numactl`. Binding "
    "instructions for all ranks should be listed in one string, separated "
    "by `/`. "
    "[legate-only, not supported with standard Python invocation]",
)


binding.add_argument(
    "--mem-bind",
    help="NUMA memories to bind each rank to. Use comma-separated integer "
    "IDs as reported by `numactl`. Binding instructions for all ranks "
    "should be listed in one string, separated by `/`. "
    "[legate-only, not supported with standard Python invocation]",
)


binding.add_argument(
    "--gpu-bind",
    help="GPUs to bind each rank to. Use comma-separated integer IDs as "
    "reported by `nvidia-smi`. Binding instructions for all ranks "
    "should be listed in one string, separated by `/`. "
    "[legate-only, not supported with standard Python invocation]",
)


binding.add_argument(
    "--nic-bind",
    help="NICs to bind each rank to. Use comma-separated device names as "
    "appropriate for the network in use. Binding instructions for all ranks "
    "should be listed in one string, separated by `/`. "
    "[legate-only, not supported with standard Python invocation]",
)


core = parser.add_argument_group("Core allocation")
core.add_argument(CPUS.name, **CPUS.kwargs)
core.add_argument(GPUS.name, **GPUS.kwargs)
core.add_argument(OMPS.name, **OMPS.kwargs)
core.add_argument(OMPTHREADS.name, **OMPTHREADS.kwargs)
core.add_argument(UTILITY.name, **UTILITY.kwargs)


memory = parser.add_argument_group("Memory allocation")
memory.add_argument(SYSMEM.name, **SYSMEM.kwargs)
memory.add_argument(NUMAMEM.name, **NUMAMEM.kwargs)
memory.add_argument(FBMEM.name, **FBMEM.kwargs)
memory.add_argument(ZCMEM.name, **ZCMEM.kwargs)
memory.add_argument(REGMEM.name, **REGMEM.kwargs)
memory.add_argument(MAX_EXCEPTION_SIZE.name, **MAX_EXCEPTION_SIZE.kwargs)
memory.add_argument(MIN_CPU_CHUNK.name, **MIN_CPU_CHUNK.kwargs)
memory.add_argument(MIN_GPU_CHUNK.name, **MIN_GPU_CHUNK.kwargs)
memory.add_argument(MIN_OMP_CHUNK.name, **MIN_OMP_CHUNK.kwargs)
memory.add_argument(FIELD_REUSE_FRACTION.name, **FIELD_REUSE_FRACTION.kwargs)
memory.add_argument(FIELD_REUSE_FREQUENCY.name, **FIELD_REUSE_FREQUENCY.kwargs)
memory.add_argument(CONSENSUS.name, **CONSENSUS.kwargs)

profiling = parser.add_argument_group("Profiling")


profiling.add_argument(
    "--profile",
    dest="profile",
    action="store_true",
    required=False,
    help="Whether to collect profiling logs",
)

profiling.add_argument(
    "--provenance",
    dest="provenance",
    action="store_true",
    required=False,
    default=None,
    help="Whether to record call provenance. "
    "Enabling call provenance will cause stack trace information to be "
    "included in Legion profiles, progress output, nvtx ranges, and some "
    "error messages. Setting --profile will automatically set --provenance.",
)


profiling.add_argument(
    "--cprofile",
    dest="cprofile",
    action="store_true",
    required=False,
    help="Profile Python execution with the cprofile module "
    "[legate-only, not supported with standard Python invocation]",
)


profiling.add_argument(
    "--nvprof",
    dest="nvprof",
    action="store_true",
    required=False,
    help="Run Legate with nvprof "
    "[legate-only, not supported with standard Python invocation]",
)


profiling.add_argument(
    "--nsys",
    dest="nsys",
    action="store_true",
    required=False,
    help="Run Legate with Nsight Systems "
    "[legate-only, not supported with standard Python invocation]",
)


profiling.add_argument(
    "--nsys-extra",
    dest="nsys_extra",
    action="append",
    default=[],
    required=False,
    help="Specify extra flags for Nsight Systems (can appear more than once). "
    "Multiple arguments may be provided together in a quoted string "
    "(arguments with spaces inside must be additionally quoted) "
    "[legate-only, not supported with standard Python invocation]",
)

logging = parser.add_argument_group("Logging")


logging.add_argument(
    "--logging",
    type=str,
    default=None,
    dest="user_logging_levels",
    help="Comma separated list of loggers to enable and their level, e.g. "
    "legate=info,foo=all,bar=error",
)


logging.add_argument(
    "--logdir",
    type=str,
    default=defaults.LEGATE_LOG_DIR,
    dest="logdir",
    help="Directory to emit logfiles to, defaults to current directory",
)


logging.add_argument(
    "--log-to-file",
    dest="log_to_file",
    action="store_true",
    required=False,
    help="Redirect logging output to a file inside --logdir",
)


debugging = parser.add_argument_group("Debugging")


debugging.add_argument(
    "--gdb",
    dest="gdb",
    action="store_true",
    required=False,
    help="Run Legate inside gdb "
    "[legate-only, not supported with standard Python invocation]",
)


debugging.add_argument(
    "--cuda-gdb",
    dest="cuda_gdb",
    action="store_true",
    required=False,
    help="Run Legate inside cuda-gdb "
    "[legate-only, not supported with standard Python invocation]",
)


debugging.add_argument(
    "--memcheck",
    dest="memcheck",
    action="store_true",
    required=False,
    help="Run Legate with cuda-memcheck "
    "[legate-only, not supported with standard Python invocation]",
)
debugging.add_argument(
    "--valgrind",
    dest="valgrind",
    action="store_true",
    required=False,
    help="Run Legate with valgrind "
    "[legate-only, not supported with standard Python invocation]",
)


debugging.add_argument(
    "--freeze-on-error",
    dest="freeze_on_error",
    action="store_true",
    required=False,
    help="If the program crashes, freeze execution right before exit so a "
    "debugger can be attached",
)


debugging.add_argument(
    "--gasnet-trace",
    dest="gasnet_trace",
    action="store_true",
    default=False,
    required=False,
    help="Enable GASNet tracing (assumes GASNet was configured with "
    "--enable-trace) "
    "[legate-only, not supported with standard Python invocation]",
)


info = parser.add_argument_group("Informational")


info.add_argument(
    "--verbose",
    dest="verbose",
    action="store_true",
    required=False,
    help="Print out each shell command before running it "
    "[legate-only, not supported with standard Python invocation]",
)


info.add_argument(
    "--bind-detail",
    dest="bind_detail",
    action="store_true",
    required=False,
    help="Print out the final invocation run by legate-bind.sh "
    "[legate-only, not supported with standard Python invocation]",
)


other = parser.add_argument_group("Other options")

other.add_argument(WINDOW_SIZE.name, **WINDOW_SIZE.kwargs)
other.add_argument(WARMUP_NCCL.name, **WARMUP_NCCL.kwargs)
other.add_argument(DISABLE_MPI.name, **DISABLE_MPI.kwargs)
other.add_argument(INLINE_TASK_LAUNCH.name, **INLINE_TASK_LAUNCH.kwargs)
other.add_argument(IO_USE_VFD_GDS.name, **IO_USE_VFD_GDS.kwargs)

other.add_argument(
    "--timing",
    dest="timing",
    action="store_true",
    required=False,
    help="Print overall process start and end timestamps to stdout "
    "[legate-only, not supported with standard Python invocation]",
)

other.add_argument(
    "--wrapper",
    dest="wrapper",
    required=False,
    action="append",
    default=[],
    help="Specify another executable (and any command-line arguments for that "
    "executable) to wrap the remaining command invocation. This wrapper will "
    "come right after the launcher invocation, and will be passed the rest of "
    "the command invocation (including any other wrappers) to execute. May "
    "contain the special string %%%%LEGATE_GLOBAL_RANK%%%% that will be "
    "replaced with the rank of the current process by bind.sh. If multiple "
    "--wrapper values are provided, they will execute in the order given. "
    "[legate-only, not supported with standard Python invocation]",
)

other.add_argument(
    "--wrapper-inner",
    dest="wrapper_inner",
    required=False,
    action="append",
    default=[],
    help="Specify another executable (and any command-line arguments for that "
    "executable) to wrap the remaining command invocation. This wrapper will "
    "come right before the command invocation (after any other "
    "wrappers) and will be passed the rest of the command invocation to "
    "execute. May contain the special string %%%%LEGATE_GLOBAL_RANK%%%% that "
    "will be replaced with the rank of the current process by bind.sh. If "
    "multiple --wrapper-inner values are given, they will execute in the "
    "order given. "
    "[legate-only, not supported with standard Python invocation]",
)

other.add_argument(
    "-m",
    "--module",
    dest="module",
    default=None,
    required=False,
    nargs=REMAINDER,
    help="Specify a Python module to load before running. Only applicable "
    "when run mode is 'python' (i.e. when running Python scripts). "
    "[legate-only, not supported with standard Python invocation]",
)


other.add_argument(
    "--dry-run",
    dest="dry_run",
    action="store_true",
    required=False,
    help="Print the full command line invocation that would be "
    "executed, without executing it "
    "[legate-only, not supported with standard Python invocation]",
)


other.add_argument(
    "--color",
    dest="color",
    action="store_true",
    required=False,
    help="Whether to use color terminal output (if rich is installed) "
    "[legate-only, not supported with standard Python invocation]",
)

other.add_argument("--version", action="version", version=__version__)

other.add_argument(
    "--info",
    action=InfoAction,
    help="Print information about the capabilities of this build of legate "
    "and immediately exit. "
    "[legate-only, not supported with standard Python invocation]",
)
