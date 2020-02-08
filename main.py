# ascii to missile test
from PIL import Image
import math as m

key = '()o|K[{]}>.:#-=$<*@ '

def split_seq(file):
    part_seq = []
    part = Image.open(file)
    coord = part.height
    for index in range(part.width//coord):
        part_seq.append(part.crop((coord*index, 0, (coord*index)+coord, coord)))
    part_seq.append(coord)
    return part_seq

def indexer(seq, key):
    if len(seq) != len(key): return False
    return dict(zip(key, seq))

def missile_maker(zipped, command='<*=={=>'):
    if len(command) < 2 or not(zipped): return False
    base = Image.new('RGBA', (zipped[' '] * len(command), zipped[' ']))
    offset = zipped[' ']
    for i in range(len(command)):
        base.paste(zipped[command[i]], (offset*i, 0), zipped[command[i]])

    return base



def main():
    seq = split_seq('images/missile_parts_small.png')
    zipped = indexer(seq, key)
    while True:
        command = input('> ')
        missile_maker(zipped, command).show()


if __name__ == '__main__':
    main()