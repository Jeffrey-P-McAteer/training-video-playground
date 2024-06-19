
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
out_map_file = f'map-arcgis-{z_level}.png'

print(f'Z_LEVEL = {z_level}')

single_tile_width_px = 256
single_tile_height_px = 256

num_x_tiles = pow(2, z_level)
num_y_tiles = pow(2, z_level)

out_map_img_width = int(num_x_tiles * single_tile_width_px)
out_map_img_height = int(num_y_tiles * single_tile_height_px)

print(f'Output map will be {out_map_img_width}x{out_map_img_height}')

out_img = PIL.Image.new('RGB', (out_map_img_width, out_map_img_height), (0, 0, 0))

for x in range(0, num_x_tiles):
  for y in range(0, num_y_tiles):
    tile_url = xyz_server_url.format(x=x, y=y, z=z_level)
    resp_jpeg_bytes = bytes()
    with urllib.request.urlopen(tile_url) as resp:
      resp_jpeg_bytes = resp.read()

    single_tile = PIL.Image.open(io.BytesIO(resp_jpeg_bytes))

    offset_x_px = x * single_tile_width_px
    offset_y_px = y * single_tile_height_px
    out_img.paste(
      single_tile, box=(offset_x_px, offset_y_px)
    )
    print('.', end='', flush=True)
  print()

print(f'Saving to {out_map_file}')

# Finally write it out
out_img.save(out_map_file)

print('Done!')
