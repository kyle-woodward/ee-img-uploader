import ee

ee.Initialize()

import logging

logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def calculator (wx:str, year:str):
    imgColl = ee.ImageCollection(f'{asset_base}/{wx}/{year}')
    percentiles = imgColl.reduce(ee.Reducer.percentile([10,50,90], ['p10','median','p90']))
    
    # ws and rh duration thresholds
    # if wx == 'ws':
    #     threshold = 10
    #     duration = something to count total days above threshold wind speed
    # if wx == 'rh':
    #     threshold = 30
    #     duration = something to count total days below threshold humidity
    
    return percentiles#.addBands(duration).resample() #.resample() to change interpolation to bicubic or bilinear?
    
if __name__ == "__main__":
    import argparse
    import textwrap

    desc = """CLI for exporting statistical reductions of large imgCollections (currently 10th percentile, median, 90th percentile)

    Usage: python Wx_stat_derivatives.py project wx year {--authenticate}
    Example: python Wx_stat_derivatives.py pyregence-ee precip 2011 --authenticate

    project - ee project to work in
    wx - data product string
    year - which year's imgCollection to reduce
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent(desc))
    parser.add_argument("project", help='-earthengine project to work in')
    parser.add_argument("wx",help='-weather variable')
    parser.add_argument("year", help='-year group')
    parser.add_argument("-a","--authenticate",dest="auth",action="store_true",help="prompt authentication pop-up to choose which EE acct to use",)

    args = parser.parse_args()
    
    parser.set_defaults(auth=False)

    project = args.project
    wx = args.wx
    year = args.year
    asset_base = f'projects/{project}/assets/conus/weather'

    out = calculator(wx, year)


    output_asset = f'{asset_base}/{wx}{year}stats'
    wx_imgColl = ee.ImageCollection(f'{asset_base}/{wx}/{year}')
    # geo_t = carbon_img.projection().transform()

    task = ee.batch.Export.image.toAsset(
            image=out,
            description=f"export_{wx}_{year}_statsImg",
            assetId=output_asset,
            region=wx_imgColl.geometry(),
            crs='EPSG:4326',
            scale=2539.703,
            maxPixels=1e12,
        )
    task.start()    
    logger.info(f'Exporting {output_asset}')
