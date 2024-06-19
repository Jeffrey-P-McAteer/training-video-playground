
import os
import sys
import subprocess
import urllib.request
import io

proj_site_packages = os.path.join(os.path.dirname(__file__), 'site-packages')
os.makedirs(proj_site_packages, exist_ok=True)

try:
  import PIL
  import PIL.Image
except:
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={proj_site_packages}', 'Pillow'
  ])
  import PIL
  import PIL.Image

# level 0 is 1x1
# level 1 is 2x2
# level 2 is 4x4
# I assume etc....
z_level = int(os.environ.get('Z_LEVEL', '4'))
xyz_server_url = 'https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

print(f'Z_LEVEL = {z_level}')


min_x = int(os.environ.get('MIN_X', '0'))
max_x = int(os.environ.get('MIN_X', str(pow(2, z_level)) ))

min_y = int(os.environ.get('MIN_Y', '0'))
max_y = int(os.environ.get('MIN_Y', str(pow(2, z_level)) ))

# Transform lat/lon to tiles
if 'LAT' in os.environ and 'LON' in os.environ:
  lat = float(os.environ['LAT'])
  lon = float(os.environ['LON'])

  lat_x_fract = (lat + 180.0) / 360.0
  lon_y_fract = (180.0 - (lon + 90.0)) / 180.0

  total_num_x_tiles = pow(2, z_level)
  total_num_y_tiles = pow(2, z_level)

  lat_x_tile_num = int(lat_x_fract * total_num_x_tiles)
  lon_y_tile_num = int(lon_y_fract * total_num_y_tiles)

  print(f'Converting {lat},{lon} to tile number {lat_x_tile_num},{lon_y_tile_num}')
  min_x = lat_x_tile_num
  min_y = lon_y_tile_num

# Allow for fixed tile output sizes
if 'WIDTH' in os.environ:
  max_x = min_x + int(os.environ['WIDTH'])

if 'HEIGHT' in os.environ:
  max_y = min_y + int(os.environ['HEIGHT'])

out_map_file = f'map-arcgis-{z_level}-{min_x}-{max_x}-{min_y}-{max_y}.png'

single_tile_width_px = 256
single_tile_height_px = 256

num_x_tiles = max_x - min_x
num_y_tiles = max_y - min_y

out_map_img_width = int(num_x_tiles * single_tile_width_px)
out_map_img_height = int(num_y_tiles * single_tile_height_px)

print(f'Output map will be {out_map_img_width}x{out_map_img_height}')

out_img = PIL.Image.new('RGB', (out_map_img_width, out_map_img_height), (0, 0, 0))

for x in range(min_x, max_x):
  for y in range(min_y, max_y):
    tile_url = xyz_server_url.format(x=x, y=y, z=z_level)
    resp_jpeg_bytes = bytes()
    with urllib.request.urlopen(tile_url) as resp:
      resp_jpeg_bytes = resp.read()

    single_tile = PIL.Image.open(io.BytesIO(resp_jpeg_bytes))

    offset_x_px = (x - min_x) * single_tile_width_px
    offset_y_px = (y - min_y) * single_tile_height_px
    out_img.paste(
      single_tile, box=(offset_x_px, offset_y_px)
    )
    print('.', end='', flush=True)
  print()

if 'display' in sys.argv:
  print('Only displaying the box...')

  out_img.show()

  print('Done!')

else:
  print(f'Saving to {out_map_file}')

  # Finally write it out
  out_img.save(out_map_file)

  print('Done!')


