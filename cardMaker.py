from PIL import Image, ImageDraw
import os

def batch_slice(image_path:str, width:int, height:int, 
                row_names:list[str], col_names:list[str],
                save_path:str, return_outputs:bool=False):
    """Slice an image into a grid of smaller images."""
    # Get the dimensions of the image
    image_path = os.path.expanduser(image_path)
    save_path = os.path.expanduser(f'{save_path}slice_output/')
    os.mkdir(save_path)
    outputs = []
    
    image = Image.open(image_path)
    image_width, image_height = image.size
    rows = len(row_names)
    cols = len(col_names)
    vert_margin = (image_height - (rows * height)) // (rows - 1)
    horiz_margin = (image_width - (cols * width)) // (cols - 1)
    for row, row_name in zip(range(rows), row_names):
        for col, col_name in zip(range(cols), col_names):
            # Calculate the coordinates of the slice
            left = col * (width + horiz_margin)
            top = row * (height + vert_margin)
            right = left + width
            bottom = top + height
            # Crop the image
            new_image = image.crop((left, top, right, bottom))
            new_image.save(f'{save_path}{col_name}_of_{row_name}.png', 'PNG')
            outputs.append(f'{save_path}{col_name}_of_{row_name}.png')
            print(f'Saved: {save_path}{col_name}_of_{row_name}.png')
    if return_outputs:
        return outputs

def remove_regions(image_path:str, region_left:int, region_top:int,
                        region_right:int, region_bottom:int,
                        starting_pts:list[int], save_path:str=None):

    # Open the image
    image = Image.open(image_path)
    if not save_path:
        save_path = image_path

    # Create a new image with the calculated dimensions
    result_image = Image.new('RGB', (image.width, image.height))
    regions_to_delete = []

    # Copy the portions of the original image that are not part of the deleted regions
    for y in range(image.height):
        for x in range(image.width):
            skip_pixel = False
            for region_left, region_top, region_right, region_bottom in regions_to_delete:
                if region_left <= x < region_right and region_top <= y < region_bottom:
                    skip_pixel = True
                    break
            if skip_pixel:
                continue  # Skip the deleted regions
            pixel_color = image.getpixel((x, y))
            result_image.putpixel((x - region_left, y - region_top), pixel_color)

    # Save the resulting image to a file
    result_image.save(image_path, 'PNG')


col_names = ['extra'] + [str(num) for num in range(2, 11)] + ['14', '11', '12', '13']
row_names = ['h', 'c', 'd', 's']
outputs = batch_slice('~/Downloads/cards.jpeg', 132, 180,
            row_names, col_names, '~/Desktop/', True)

