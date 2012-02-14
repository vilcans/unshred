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

def get_correlation(left_shred, right_shred):
    """Gets how well left_shred fits to the left of right_shred.
    left_shred and right_shred are shred indexes.
    """
    difference = 0.0
    for y in xrange(height):
        left_pixel = get_pixel(shred_width * (left_shred + 1) - 1, y)
        right_pixel = get_pixel(shred_width * right_shred, y)
        difference += get_color_distance(left_pixel, right_pixel)
    return 1.0 / (difference + 1)


def save(sequence):
    unshredded = Image.new('RGB', image.size)
    for i, shred_index in enumerate(sequence):
        shred_x1, shred_y1 = shred_width * shred_index, 0
        shred_x2, shred_y2 = shred_x1 + shred_width, height
        region = image.crop((shred_x1, shred_y1, shred_x2, shred_y2))
        unshredded.paste(region, (shred_width * i, 0))
    unshredded.save('unshredded.png')


correlations = []
for left in xrange(number_of_shreds):
    #correlations.append([])
    for right in xrange(number_of_shreds):
        if left == right:
            continue
        correlation = get_correlation(left, right)
        #print left, right, correlation
        #correlations[-1].append((correlation, left, right))
        correlations.append((correlation, left, right))

correlations.sort(reverse=True)
rights = {}  # Maps from left shred to the right
lefts = {}  # Maps from right shred to the left
for _, left_shred, right_shred in correlations:
    if left_shred in rights or right_shred in lefts:
        continue
    rights[left_shred] = right_shred
    lefts[right_shred] = left_shred
    if len(rights) == number_of_shreds:
        break


sequence = []
i = 8
for _ in xrange(number_of_shreds):
    sequence.append(i)
    i = rights[i]

save(sequence)
