## Upload workflow

1. upload - ee_upload_Wx.py
2. verify - check_wx_uploads.py
3. reduce - Wx_stat_derivatives.py

### upload - ee_upload_Wx.py

CLI for uploading Vulnerability tiled images into respective Earth Engine ImageCollections

e.x. want to upload all slope files on bucket into a slope ImageCollection
ee_upload_vuln_files.py slope mean

    python ee_upload_Wx.py project product bucket pyramid year

    project - ee project to work in
    product - data product to retrieve from the google storage bucket
    pyramid - pyramiding policy for the uploaded asset, ex: mean, mode
    year - year group
