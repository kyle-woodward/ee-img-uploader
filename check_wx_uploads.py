#%%

import logging
import subprocess

logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    import argparse
    import textwrap

    desc = """
    CLI for checking on missing images in an EE imageCollection - checks against a set of images that were supposed to have been uploaded by ee_upload_Wx.py

    Usage python check_wx_uploads.py project wx year_st year_end {--reupload} {--authenticate}

    example: python check_wx_uploads.py pyregence-ee precip 2011 2012 --reupload --authenticate
    
    set --reupload flag if you want to send the img upload tasks, otherwise it just lists the files that are missing
    
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(desc),
    )
    parser.add_argument("project", type=str, help="-earthengine project to work in")
    parser.add_argument("wx", type=str, help="-weather variable")
    parser.add_argument("year_st", type=int, help="-year start")
    parser.add_argument("year_end", type=int, help="-year end")
    parser.add_argument(
        "-r",
        "--reupload",
        dest="reupload",
        action="store_true",
        help="flag to reupload missing files the script finds",
    )
    parser.add_argument(
        "-a",
        "--authenticate",
        dest="auth",
        action="store_true",
        help="prompt authentication pop-up to choose which EE acct to use",
    )

    args = parser.parse_args()

    parser.set_defaults(reupload=False)
    parser.set_defaults(auth=False)

    project = args.project
    wx = args.wx
    year_st = args.year_st
    year_end = args.year_end
    reupload = args.reupload

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

    asset_base = f"projects/{project}/assets/conus/weather"

    # can run this to double-check all files from bucket got uploaded to its EE imagecollection and re-upload if desired
    import os
    import subprocess

    gs_root = "gs://landfire/weather/merged"

    years = range(year_st, year_end)

    logger.info(years)
    for year in years:
        regex = f"{wx}*"

        list_of_files_gs = (
            os.popen(f"gsutil ls {gs_root}/{year}*/*{regex}.tif")
            .read()
            .split("\n")[0:-1]
        )
        list_of_imgs_ee = (
            os.popen(
                f"earthengine ls projects/{project}/assets/conus/weather/{wx}/{year}"
            )
            .read()
            .split("\n")[0:-1]
        )
        logger.info(f"{year} {wx} files on gs: {len(list_of_files_gs)}")
        logger.info(f"{year} {wx} imgs on ee imgcoll: {len(list_of_imgs_ee)}")

        if len(list_of_files_gs) != len(list_of_imgs_ee):

            list_of_files_gs = [
                os.path.basename(f).split(".")[0] for f in list_of_files_gs
            ]
            list_of_imgs_ee = [os.path.basename(f) for f in list_of_imgs_ee]

            left_out_files = [
                (gs_root + "/" + f[0:6] + "/" + f)
                for f in list_of_files_gs
                if f not in list_of_imgs_ee
            ]
            len_files = len(left_out_files)
            logger.info(f"gs files not in its ee imgcollection:{len_files}")

            collection_path = f"projects/{project}/assets/conus/weather/{wx}/{year}"

            # re-upload
            if reupload:
                for file in left_out_files:
                    # logger.info(file)
                    asset_name = os.path.basename(file).split(".tif")[0]
                    ee_upload_cmd = f"earthengine upload image --asset_id={collection_path}/{asset_name} --pyramiding_policy=mean --bands={wx} {file}.tif"
                    # logger.info(ee_upload_cmd)
                    proc = subprocess.Popen(
                        ee_upload_cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )

                    out, err = proc.communicate()
                    if err:
                        logger.info(f"ERROR {err}")
                    current_file_index = left_out_files.index(file)
                    if current_file_index == 0:
                        logger.info(f"Starting ingestion 1/{len_files}")
                    elif current_file_index % 250 == 0:
                        logger.info(
                            f"Started {current_file_index}/{len_files}, Remaining tasks: {len_files-current_file_index}"
                        )

                logger.info(f"///////// FIN //////////////")
