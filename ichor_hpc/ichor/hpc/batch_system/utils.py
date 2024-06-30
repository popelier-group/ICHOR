import json
from pathlib import Path
from typing import List, Optional

from ichor.hpc.batch_system.batch_system import Job, JobID


def read_jid(jid_file: Optional[Path] = None) -> List[JobID]:
    if jid_file is None:
        import ichor.hpc.global_variables

        jid_file = ichor.hpc.global_variables.FILE_STRUCTURE["jid"]

    if jid_file.exists():
        with open(jid_file, "r") as f:
            try:
                jids = json.load(f)
            except json.JSONDecodeError:
                jids = []
            return [
                JobID(
                    script=jid["script"],
                    id=jid["id"],
                )
                for jid in jids
            ]

    return []


def delete_jobs():
    """Delete all jobs that were queued up to run.
    This function reads the ichor.hpc.global_variables.FILE_STRUCTURE["jid"]
    file, which contains the names of all submitted jobs."""
    import ichor.hpc.global_variables

    jid_file = ichor.hpc.global_variables.FILE_STRUCTURE["jid"]
    jids = read_jid()
    for jid in jids:
        ichor.hpc.global_variables.BATCH_SYSTEM.delete(jid)
        print(f"Deleted {jid}")

    with open(jid_file, "w") as f:
        f.write("[]")


def get_current_jobs() -> List[Job]:
    import ichor.hpc.global_variables

    all_jobs = ichor.hpc.global_variables.BATCH_SYSTEM.get_queued_jobs()
    ichor_jobs = read_jid(ichor.hpc.global_variables.FILE_STRUCTURE["jid"])
    ichor_job_ids = [job.id for job in ichor_jobs]

    return [job for job in all_jobs if job.id in ichor_job_ids]


def display_status_of_running_jobs():
    ichor_queued_jobs = get_current_jobs()

    for job in ichor_queued_jobs:
        print(job)

    print()
    print(f"Total Jobs: {len(ichor_queued_jobs)}")
    print(
        f"Running Jobs: {len([j for j in ichor_queued_jobs if j.state == 'Running'])}"
    )
    print(
        f"Queueing Jobs: {len([j for j in ichor_queued_jobs if j.state == 'Queueing'])}"
    )
    print(
        f"Holding Jobs: {len([j for j in ichor_queued_jobs if j.state == 'Holding'])}"
    )
