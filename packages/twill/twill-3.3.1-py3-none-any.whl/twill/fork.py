"""The twill multiprocess execution system."""

import os
import sys
import time
from argparse import ArgumentParser
from pickle import dump, load

from twill import execute_file, set_log_level


def main() -> None:
    """Run twill scripts in parallel."""
    try:
        if sys.platform == "win32":
            raise AttributeError
        fork = os.fork
    except AttributeError:
        sys.exit("Error: Must use Unix to be able to fork processes.")

    parser = ArgumentParser()
    add = parser.add_argument
    add(
        "-u",
        "--url",
        action="store",
        dest="url",
        help="start at the given URL before each script",
    )
    add(
        "-n",
        "--number",
        action="store",
        dest="number",
        default=1,
        type=int,
        help="number of times to run the given script(s)",
    )
    add(
        "-p",
        "--processes",
        action="store",
        dest="processes",
        default=1,
        type=int,
        help="number of processes to execute in parallel",
    )
    add(
        "scripts",
        metavar="SCRIPT",
        nargs="+",
        help="one or more twill scripts to execute",
    )

    args = parser.parse_args()

    # make sure that the current working directory is in the path
    if "" not in sys.path:
        sys.path.append("")

    average_number = args.number // args.processes
    last_number = average_number + args.number % args.processes
    child_pids = []
    is_parent = True
    repeat = 0

    # start a bunch of child processes and record their pids in the parent
    for i in range(args.processes):
        pid = fork()
        if pid:
            child_pids.append(pid)
        else:
            repeat = average_number if i else last_number
            is_parent = False
            break

    # set the children up to run and record their stats
    failed = False

    if is_parent:
        time.sleep(1)

        total_time = total_exec = 0

        # iterate over all the child pids, wait until they finish,
        # and then sum statistics
        for child_pid in child_pids[:]:
            pid, status = os.waitpid(child_pid, 0)
            if status or pid != child_pid:  # failure
                print(
                    f"[twill-fork parent: process {child_pid} FAILED:"
                    f" exit status {status}]"
                )
                print(
                    "[twill-fork parent:"
                    " (not counting stats for this process)]"
                )
                failed = True
            else:  # record statistics, otherwise
                filename = f".status.{child_pid}"
                with open(filename, "rb") as fp:
                    this_time, n_executed = load(fp)  # noqa: S301
                os.unlink(filename)  # noqa: PTH108
                total_time += this_time
                total_exec += n_executed

        # summarize
        print("\n----\n")
        print(f"number of processes: {args.processes}")
        print(f"total executed: {total_exec}")
        print(f"total time to execute: {total_time:.2f} s")
        if total_exec:
            avg_time = 1000 * total_time / total_exec
            print(f"average time: {avg_time:.2f} ms")
        else:
            print("(nothing completed, no average!)")
        print()

    else:
        pid = os.getpid()
        print(f"[twill-fork: pid {pid} : executing {repeat} times]")

        start_time = time.time()

        set_log_level("warning")
        for _i in range(repeat):
            for filename in args.scripts:
                execute_file(filename, initial_url=args.url)

        end_time = time.time()
        this_time = end_time - start_time

        # write statistics
        filename = f".status.{pid}"
        with open(filename, "wb") as fp:
            info = (this_time, repeat)
            dump(info, fp)

    sys.exit(-1 if failed else 0)


if __name__ == "__main__":
    main()
