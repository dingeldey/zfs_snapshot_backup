import argparse
import datetime
import os.path
import subprocess
import sys

from utils.rsync_policy import RsyncPolicy
from utils.rsync_caller import RsyncCaller


def make_snap_shots(dataset_name: str, time: str):
    print(f"Creating ZFS snapshot with name {dataset_name}@{time}")

    with subprocess.Popen(['zfs', 'snapshot', f"{dataset_name}@{time}"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
                          universal_newlines=True) as p:
        for line in p.stdout:
            print(line)
        exit_code = p.wait()
        if exit_code != 0:
            raise Exception('Failed to create ZFS snapshot')


def datetime_to_string(dtime: datetime.datetime):
    timestamp = '{:%Y-%m-%d_%H-%M-%S}'.format(dtime)
    return timestamp


def main():
    parser = argparse.ArgumentParser()
    adding_parser_arguments(parser)
    args, unknown = parser.parse_known_args()

    if args.dataset[0] == os.path.sep:
        raise Exception("dataset may not start with os.path.sep, this will be appended wheb actually running the rsync command")

    timestamp = datetime_to_string(datetime.datetime.now())
    try:
        if args.take_snapshot:
            make_snap_shots(args.dataset, timestamp)
        if args.quit_after_snapshot:
            sys.exit(0)

        rsync_policy: RsyncPolicy = RsyncPolicy(args.rsync_flag)
        RsyncCaller.sync_data(args.source, f"/{args.dataset}", rsync_policy)

    except Exception as e:
        print(e)
        sys.exit(1)


def adding_parser_arguments(parser):
    parser.add_argument('-d', '--dataset', help="takes a snapshot of the specified dataset(s)")
    parser.add_argument('-q', '--quit_after_snapshot', action='store_true', help="Terminates program after snapshot")
    parser.add_argument('-t', '--take_snapshot', action='store_true', help="Indicates if a snapshot of the dataset shall be performed prior to rsync.")
    parser.add_argument('-s', '--source', action='append', help="Specify a source")
    parser.add_argument('-r', '--rsync_flag', action='append', metavar='rsync_flag', help="Flag to be be passed to rsync. "
                                                                                            "Use like this -f='--delete'")


if __name__ == '__main__':
    main()
