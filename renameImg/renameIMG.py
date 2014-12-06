#!/bin/env python
import argparse
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime, timedelta
from os.path import exists
from os import rename

def get_exifdatetime(fn):
    i = Image.open(fn)
    info = i._getexif()
    return info[306]

def get_datetime(str_datetime, fmt="%Y:%m:%d %H:%M:%S"):
    return datetime.strptime(str_datetime, fmt)

def file_exists(fn):
    return exists(fn)


parser = argparse.ArgumentParser(description='Rename images based on their timestamp.')
parser.add_argument('files', metavar='F', type=str, nargs='+',
                   help='list of files')
parser.add_argument('-e', '--exif', action='store_true', default=False,
                    help='Only print exif DateTime value of each file')
parser.add_argument('-p', '--pretend', action='store_true', default=False,
                    help='Do not rename, just print old and new name')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Verbose mode')

parser.add_argument('-d', '--days', type=int,
                    help='Add this number of days to the timestamp')
parser.add_argument('-S', '--seconds', type=int,
                    help='Add this number of seconds to the timestamp')

args = parser.parse_args()


# Parse date change arguments
args_add_days = args.days if args.days else 0
args_add_seconds = args.seconds if args.seconds else 0

if args.verbose:
    print("Will increment the timestamp by %d days and %s seconds" % (args_add_days, args_add_seconds))

args_timedelta = timedelta(args_add_days, args_add_seconds)



# Start
#######

for fn in args.files:
    try:
        exifdatetime = get_exifdatetime(fn)
    except:
        print("Unable to parse file %s" % fn)
    

    # If --exif is set, just print exif and continue to next file
    if args.exif:
        print(exifdatetime)
        continue

    # Translade the date
    dt = get_datetime(exifdatetime)
    new_dt = dt + args_timedelta

    # Get the extension of the file
    fn_ext = fn[fn.rfind(".") + 1:].lower()

    # Create the new name of the file
    
    base_name = new_dt.strftime("%Y-%m-%d_%H-%M-%S")
    new_fn = base_name + "." + fn_ext

    new_i = 1
    while file_exists(new_fn):
        new_fn = base_name + "-" + str(new_i) + "." + fn_ext


    # Rename the file
    if not args.pretend:
        rename(fn, new_fn)

    if args.verbose or args.pretend:
        print("Rename %s\t to %s" % (fn, new_fn))
    
    
