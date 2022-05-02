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


def calculator (product:str, year:str):
    imgColl = ee.ImageCollection(f'{asset_base}/{product}/{year}')
    percentiles = imgColl.reduce(ee.Reducer.percentile([10,50,90], ['p10','median','p90']))
    
    
    return percentiles
    
if __name__ == "__main__":
    import argparse
    import textwrap

    desc = """CLI for exporting statistical reductions of large imgCollections (currently 10th percentile, median, 90th percentile)

    Usage: python imgColl_stat_derivatives.py project product year {--authenticate}
    Example: python imgColl_stat_derivatives.py pyregence-ee precip 2011 --authenticate

    project - ee project your imgColl is in
    product - data product string
    year - which year's imgCollection to reduce (assumes each imgColl is one year's worth of data)
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent(desc))
    parser.add_argument("project", help='-earthengine project to your imgColl is in')
    parser.add_argument("product",help="-img collection product (file's basename e.g. precip)")
    parser.add_argument("year", help="-year imgColl to reduce (assumes each imgColl is one year's worth of data)")
    parser.add_argument("-a","--authenticate",dest="auth",action="store_true",help="prompt authentication pop-up to choose which EE acct to use",)

    args = parser.parse_args()
    
    parser.set_defaults(auth=False)

    project = args.project
    product = args.product
    year = args.year
    asset_base = f'projects/{project}/assets/conus/weather'

    out = calculator(product, year)


    output_asset = f'{asset_base}/{product}{year}stats'
    wx_imgColl = ee.ImageCollection(f'{asset_base}/{product}/{year}')
    # geo_t = carbon_img.projection().transform()

    task = ee.batch.Export.image.toAsset(
            image=out,
            description=f"export_{product}_{year}_statsImg",
            assetId=output_asset,
            region=wx_imgColl.geometry(),
            crs='EPSG:4326',
            scale=2539.703,
            maxPixels=1e12,
        )
    task.start()    
    logger.info(f'Exporting {output_asset}')
