# ee-img-uploader

![ee-uploader-gif](https://user-images.githubusercontent.com/51868526/167019407-830dfbe3-5284-4b0f-9b10-3d8450b0fe7a.gif)

## Upload workflow

1. upload - ee_upload_imgs.py
2. verify - check_img_uploads.py
3. reduce - imgColl_stat_derivatives.py

### __upload - ee_upload_imgs.py__

CLI for batch uploading A LOT of images into EE imageCollections, here specifically in our examples, weather time series data

    Usage: python ee_upload_imgs.py project product pyramiding year_st
    Example: python ee_upload_imgs.py pyregence-ee precip mean 2017



### __verify - check_img_uploads.py__

CLI for checking on missing images in an EE imageCollection - checks against a set of images that were supposed to have been uploaded by ee_upload_imgs.py

    Usage: python check_img_uploads.py project product year_st year_end {--reupload} {--authenticate}
    Example: python check_img_uploads.py pyregence-ee precip 2011 2012 --reupload --authenticate

### __reduce - imgColl_stat_derivatives.py__

CLI for exporting statistical reductions of large imgCollections (currently 10th percentile, median, 90th percentile)

    Usage: python imgColl_stat_derivatives.py project product year {--authenticate}
    Example: python imgColl_stat_derivatives.py pyregence-ee precip 2011 --authenticate
