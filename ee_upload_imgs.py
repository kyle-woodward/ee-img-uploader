#%%
import os
import sys
import subprocess
import logging
import ee
import time

ee.Initialize()

logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def ee_path_exists(path: str):
    """checks if a ee paths exists using the cli"""
    cmd = ["earthengine", "ls", path]
    results = subprocess.run(cmd, capture_output=True, text=True)
    return "not found." not in results.stdout


def make_folders(path: str):
    """recursively checks that all folders in a path exist and makes the folder if it doesn't."""
    level_down_path = "/".join(path.split("/")[:-1])
    exists = ee_path_exists(path)
    if exists:
        return
    if not ee_path_exists(level_down_path):
        make_folders(level_down_path)
    if not exists:
        logger.info(f"Making folder: {path}")
        cmd = ["earthengine", "create", "folder", path]
        subprocess.run(cmd)


def parse_task_response(response: str):
    """returns the task id from an ee upload tast initiated via the ee cli.

    Args:
        response (str): Output from EE cli task (e.g. Started upload task with ID: 7TCCSJHNN2OIZTUSZF74ZEUC)

    Returns:
        str: the task id (e.g 7TCCSJHNN2OIZTUSZF74ZEUC)
    """
    return response.split(" ")[-1].strip()


def remove_finished_tasks(task_list: list, project: str) -> list:
    # project = "pyregence-ee"
    # operation = "VDCQ5PSQESNLU2ENMVMP46JY"
    stack = []
    for operation in task_list:
        op_str = f"projects/{project}/operations/{operation}"
        tasks = ee.data.getOperation(op_str)
        if tasks["metadata"]["state"] != "SUCCEEDED":
            stack.append(operation)
    return stack


def wait_until_completed(task_list: list, project: str, count: int) -> list:
    in_size = len(task_list)
    seconds_to_sleep = 300
    target_task_list_size = in_size - count
    while len(task_list) > target_task_list_size:
        logger.info(
            f"waiting {seconds_to_sleep / 60} minutes while tasks finish ingesting"
        )
        logger.info(
            f"task list size: {len(task_list)}, target task list size: {target_task_list_size}"
        )
        time.sleep(seconds_to_sleep)
        task_list = remove_finished_tasks(task_list, project)

    return task_list


def batch_upload_img_to_imgColl(
    project: str, product: str, pyramid: str, year: int
):

    pyramid = str.lower(pyramid)

    # get list of files for a given product
    gs_root = "gs://landfire/weather/merged" # will need to change this to use another bucket
    regex = f"{product}*"
    gsutil_ls_cmd = f"gsutil ls {gs_root}/{year}*/*{regex}.tif"
    proc = subprocess.Popen(
        gsutil_ls_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    out, err = proc.communicate()

    # convert binary result to list of str
    files = out.decode().split("\n")[:-1]
    len_files = len(files)

    logger.info(f"{len_files} files found for {product}")

    folder_path = f"projects/{project}/assets/conus/weather/{product}"

    logger.info(f"Checking folders at {folder_path}")
    make_folders(folder_path)

    collection_path = f"{folder_path}/{year}"
    if not ee_path_exists(collection_path):
        # if an img collection has not been made for it, create it
        create_collection_cmd = (
            f"earthengine create collection {collection_path}"
        )

        logger.info(f"Creating Image Collection at {collection_path}")

        proc = subprocess.Popen(
            create_collection_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        out, err = proc.communicate()

    # for each tif file in list of product files on bucket, start an upload task to upload to the imgColl
    running_tasks = []

    for file in files:
        asset_name = os.path.basename(file).split(".")[0]

        ee_upload_cmd = f"earthengine upload image --force --asset_id={collection_path}/{asset_name} --pyramiding_policy={pyramid} --bands={product} {file}"

        proc = subprocess.Popen(
            ee_upload_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        out, err = proc.communicate()

        # catch errors and log it to console
        if err:
            logger.info(f"ERROR {err}")
        else:
            # add the task id to the stack
            task_id = parse_task_response(out)
            running_tasks.append(task_id)

        # check how many tasks have been submitted
        # the maximum number of tasks to have in the pipeline at one time
        task_threshold = 2750
        # the number of tasks that need to finish ingestion before adding more to the pipeline
        task_wait_until_completed = 300
        if len(running_tasks) > task_threshold:
            logger.info(
                f"task threshold met, waiting until {task_wait_until_completed} tasks are ingested."
            )
            # clean task list
            running_tasks = remove_finished_tasks(running_tasks, project)
            # wait until tasks complete
            running_tasks = wait_until_completed(
                running_tasks, project, task_wait_until_completed
            )

        current_file_index = files.index(file)

        if current_file_index == 0:
            logger.info(f"Starting ingestion 1/{len_files}")
        elif current_file_index % 250 == 0:
            logger.info(
                f"Started {current_file_index}/{len_files}, Remaining tasks: {len_files-current_file_index}"
            )

    logger.info("///////// FIN //////////////")


if __name__ == "__main__":
    import argparse
    import textwrap

    desc = """ CLI for batch uploading A LOT of images into EE imageCollections, here specifically weather timeseries data
    
    Usage python ee_upload_imgs.py project product pyramiding year_st 

    example: python ee_upload_imgs.py pyregence-ee precip mean 2017
  """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(desc),
    )
    parser.add_argument("project", help="-ee project to upload assets to")
    parser.add_argument(
        "product",
        help="-img collection product (file's basename e.g. precip)",
    )
    parser.add_argument(
        "pyramid",
        help="-pyramiding policy for the uploaded asset, ex: mean, mode",
    )
    parser.add_argument("year", help="-year imgColl to upload (assumes each imgColl is one year's worth of data)")
    parser.add_argument(
        "-a",
        "--authenticate",
        dest="auth",
        action="store_true",
        help="prompt authentication pop-up to choose which EE acct to use",
    )
    args = parser.parse_args()

    parser.set_defaults(auth=False)

    # prompt user interactive authentication
    if args.auth:
        logger.info(
            "Choose your EE account in the Authentication pop-up and paste the OAuth token in the console"
        )
        proc = subprocess.Popen(
            "earthengine authenticate",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        out, err = proc.communicate()

    batch_upload_img_to_imgColl(
        args.project, args.product, args.pyramid, args.year
    )
