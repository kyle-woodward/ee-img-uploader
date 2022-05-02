# ee-img-uploader

## Upload workflow

1. upload - ee_upload_imgs.py
2. verify - check_img_uploads.py
3. reduce - imgColl_stat_derivatives.py

### __upload - ee_upload_imgs.py__

CLI for batch uploading A LOT of images into EE imageCollections, here specifically weather timeseries data

   Usage python ee_upload_imgs.py project product pyramiding year_st

   example: python ee_upload_imgs.py pyregence-ee precip mean 2017

positional arguments:
  project             -ee project to upload assets to
  product             -img collection product (file's basename e.g. precip)
  pyramid             -pyramiding policy for the uploaded asset, ex: mean, mode
  year                -year imgColl to upload (assumes each imgColl is one year's worth of data)

optional arguments:
  -h, --help          show this help message and exit
  -a, --authenticate  prompt authentication pop-up to choose which EE acct to use


### __verify - check_img_uploads.py__

CLI for checking on missing images in an EE imageCollection - checks against a set of images that were supposed to have been uploaded by ee_upload_imgs.py

Usage python check_img_uploads.py project wx year_st year_end {--reupload} {--authenticate}

example: python check_img_uploads.py pyregence-ee precip 2011 2012 --reupload --authenticate

set --reupload flag if you want to send the img upload tasks, otherwise it just lists the files that are missing

**assumes each imgColl is one year's worth of data

positional arguments:
  project             -earthengine project to upload assets to
  product             -img collection product (file's basename e.g. precip)
  year_st             -year start
  year_end            -year end (exclusive)

optional arguments:
  -h, --help          show this help message and exit
  -r, --reupload      flag to reupload missing files the script finds
  -a, --authenticate  prompt authentication pop-up to choose which EE acct to use

### __reduce - imgColl_stat_derivatives.py__

CLI for exporting statistical reductions of large imgCollections (currently 10th percentile, median, 90th percentile)

    Usage: python imgColl_stat_derivatives.py project wx year {--authenticate}
    Example: python imgColl_stat_derivatives.py pyregence-ee precip 2011 --authenticate

    project - ee project your imgColl is in
    product - data product string
    year - which year's imgCollection to reduce (assumes each imgColl is one year's worth of data)

positional arguments:
  project             -earthengine project to your imgColl is in
  product             -img collection product (file's basename e.g. precip)
  year                -year imgColl to reduce (assumes each imgColl is one year's worth of data)

optional arguments:
  -h, --help          show this help message and exit
  -a, --authenticate  prompt authentication pop-up to choose which EE acct to use
