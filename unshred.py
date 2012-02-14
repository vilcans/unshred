#!/usr/bin/python

from math import sqrt
from PIL import Image

image = Image.open('TokyoPanoramaShreddedNumbered.png')
data = image.getdata()
width, height = image.size

shred_width = 32
number_of_shreds = width // shred_width
assert number_of_shreds * shred_width == width, \
    'image width must be multiple of ' + shred_width

debug_image = Image.new('RGB', image.size)

def get_pixel(x, y):
    assert y >= 0 and y < height, 'y=%s' % y
    assert x >= 0 and x < width, 'x=%s' % x
    pixel = data[y * width + x]
    return pixel[:3]

def get_color_distance(c1, c2):
    """Gets the euclidian distance between two (color) vectors."""
    return sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

cached_differences = {}
def get_difference(left_shred, right_shred):
    """Gets how badly left_shred fits to the left of right_shred.
    left_shred and right_shred are shred indexes.
    """
    if (left_shred, right_shred) in cached_differences:
        return cached_differences[(left_shred, right_shred)]
    difference = 0.0
    left_x = shred_width * (left_shred + 1) - 1
    right_x = shred_width * right_shred
    for y in xrange(1, height - 1):
        difference += min((
            get_color_distance(get_pixel(left_x, y), get_pixel(right_x, y - 1)),
            get_color_distance(get_pixel(left_x, y), get_pixel(right_x, y)),
            get_color_distance(get_pixel(left_x, y), get_pixel(right_x, y + 1))
        ))
    cached_differences[(left_shred, right_shred)] = difference
    return difference

def save(sequence, filename):
    print 'saving', filename
    unshredded = Image.new('RGB', image.size)
    for i, shred_index in enumerate(sequence):
        shred_x1, shred_y1 = shred_width * shred_index, 0
        shred_x2, shred_y2 = shred_x1 + shred_width, height
        region = image.crop((shred_x1, shred_y1, shred_x2, shred_y2))
        unshredded.paste(region, (shred_width * i, 0))
    unshredded.save(filename)


best_right = [None] * number_of_shreds
for left in xrange(number_of_shreds):
    diffs = []
    for right in xrange(number_of_shreds):
        if left == right:
            continue
        difference = get_difference(left, right)
        diffs.append((difference, right))
    best_right[left] = sorted(diffs)[0]

sequences = []
for leftmost in xrange(number_of_shreds):
    sequence = [leftmost]
    i = best_right[leftmost][1]
    while len(sequence) != number_of_shreds:
        sequence.append(i)
        i = best_right[i][1]
    total_difference = sum(
        get_difference(sequence[i], sequence[i + 1])
        for i in range(number_of_shreds - 1)
    )
    sequences.append((total_difference, sequence))

sequences.sort()
print sequences
save(sequences[0][1], 'unshredded.png')
