#%%
import logging

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

    desc = """CLI for uploading Vulnerability tiled images into respective Earth Engine ImageCollections

        e.x. want to upload all slope files on bucket into a slope ImageCollection
            ee_upload_vuln_files.py slope mean
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent(desc))
    parser.add_argument("project", type=str,help='-earthengine project to work in')
    parser.add_argument("wx",type=str,help='-weather variable')
    parser.add_argument("year_st", type=int, help='-year start')
    parser.add_argument("year_end",type=int, help='-year end')
    parser.add_argument(
        "-r",
        "--reupload",
        dest="reupload",
        action="store_true",
        help="flag to reupload missing files the script finds",
    )
    args = parser.parse_args()
    
    parser.set_defaults(reupload=False)

    project = args.project
    wx = args.wx
    year_st = args.year_st
    year_end = args.year_end
    reupload = args.reupload
    
    asset_base = f'projects/{project}/assets/conus/weather'


    #can run this to double-check all files from bucket got uploaded to its EE imagecollection and re-upload if desired
    import os
    import subprocess
    
    gs_root = 'gs://landfire/weather/merged'
    product_list = ['precip']
    
    years = range(year_st,year_end)
    
    logger.info(years)
    for year in years:
        regex  = f'{wx}*'

        list_of_files_gs = os.popen(f'gsutil ls {gs_root}/{year}*/*{regex}.tif').read().split('\n')[0:-1]
        list_of_imgs_ee = os.popen(f'earthengine ls projects/{project}/assets/conus/weather/{wx}/{year}').read().split('\n')[0:-1]
        logger.info(f'{year} {wx} files on gs: {len(list_of_files_gs)}')
        logger.info(f'{year} {wx} imgs on ee imgcoll: {len(list_of_imgs_ee)}')

        if len(list_of_files_gs) != len(list_of_imgs_ee):

            list_of_files_gs = [os.path.basename(f).split('.')[0] for f in list_of_files_gs]
            list_of_imgs_ee = [os.path.basename(f) for f in list_of_imgs_ee]

            left_out = [os.path.join(gs_root, f[0:6], f) for f in list_of_files_gs if f not in list_of_imgs_ee]
            logger.info(f'gs files not in its ee imgcollection:\n{left_out}')
            
            # re-upload
            collection_path = f'projects/pyregence-ee/assets/conus/weather/{wx}/{year}'
            if reupload:
                for f in left_out:
                    asset_name = os.path.basename(f).split('.tif')[0]
                    ee_upload_cmd = f'earthengine upload image --asset_id={collection_path}/{asset_name} --pyramiding_policy=mean --bands={wx} {f}.tif'
                    logger.info(ee_upload_cmd)
                    proc = subprocess.Popen(
                            ee_upload_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                            )
            
                    out, err = proc.communicate()
            
        #break
# %%
