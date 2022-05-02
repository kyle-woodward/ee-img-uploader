# ee-img-uploader

## Upload workflow

1. upload - ee_upload_imgs.py
2. verify - check_img_uploads.py
3. reduce - imgColl_stat_derivatives.py

### upload - ee_upload_Wx.py

CLI for batch uploading A LOT of images into EE imageCollections, here specifically weather timeseries data
    
    Usage: python ee_upload_Wx.py project product pyramid year
    Example: python ee_upload_Wx.py pyregence-ee precip mean 2011

    project - ee project to work in
    product - data product string to retrieve from the google storage bucket (common file basename to use in regex expression)
    pyramid - pyramiding policy for the uploaded asset, ex: mean, mode
    year - year group


### verify - check_wx_uploads.py

CLI for checking on missing images in an EE imageCollection - checks against a set of images that were supposed to have been uploaded by ee_upload_Wx.py

*sometimes image upload tasks fail for no good reason randomly, so this is nice way to only re-upload the failed ones*

    Usage: python check_wx_uploads.py project wx year_st year_end {--reupload}
    Example: python check_wx_uploads.py pyregence-ee precip 2011 2012 --reupload
    
    project - ee project to work in
    wx - data product string
    -year_st - start year range 
    -year_end - end of year range (exclusive)
    -r --reupload (optional) - flag if you want to send the img upload tasks (otherwise it counts missing files and stops)

### reduce - Wx_stat_derivatives.py

CLI for exporting statistical reductions of large imgCollections (currently 10th percentile, median, 90th percentile)

    Usage: python Wx_stat_derivatives.py project wx year
    Example: python Wx_stat_derivatives.py pyregence-ee precip 2011

    project - ee project to work in
    wx - data product string
    year - which year's imgCollection to reduce
