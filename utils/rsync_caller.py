from utils.rsync_policy import RsyncPolicy
from typing import List, Tuple
import subprocess
import os
from utils.changesummary import ChangeSummary


class RsyncCaller:
    @staticmethod
    def sync_data(sources: List[str], dataset_name: str, rsync_policy: RsyncPolicy) -> Tuple[ChangeSummary, str]:
        """
        Making the actual rsync call.
        @param sources: List of source paths
        @param dataset_name: backup path for the current timestamp.
        @param rsync_policy: Policy in which the parameters of the rsync call are assembled.
        @return: 1) Change summary of rsync. Can be used to see if a really large amount of files was removed.
                 2) Used rsync cmd
        """

        RsyncCaller.__check_if_sources_are_empty(sources)
        print(f"Mirroring {sources} to {dataset_name}.")
        rsync_cmd = "rsync "
        for flag in rsync_policy.parameters:
            rsync_cmd = rsync_cmd + " " + flag
        for source in sources:
            rsync_cmd = rsync_cmd + " " + source

        rsync_cmd = rsync_cmd + " " + dataset_name
        print(f"rsync command reads: {rsync_cmd}")
        out = ""
        with subprocess.Popen(['rsync', *rsync_policy.parameters, *sources, dataset_name],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
                              universal_newlines=True) as p:
            for line in p.stdout:
                print(line.strip("\n"))
            exit_code = p.wait()
            if exit_code != 0:
                raise Exception(f'Rsync Failed with error code {exit_code}')

        summary: ChangeSummary = ChangeSummary(out)
        return summary, rsync_cmd

    @staticmethod
    def __check_if_sources_are_empty(sources: List[str]):
        """
        Checks if sources are not empty. If it encounters an empty source it raises an
        exception to cause the backup to fail.
        @param sources: List of source paths.
        """
        for source in sources:
            if os.path.isfile(source):
                continue

            if not os.path.isdir(source) or os.path.isfile(source):
                raise Exception("Specified source does not exist.")

            # check if empty
            if not any(os.scandir(source)):
                raise Exception("Directory is empty. This causes a backup to fail")

