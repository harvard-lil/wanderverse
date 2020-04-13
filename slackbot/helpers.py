import random

colors = ["red", "orange", "yellow", "green", "blue", "purple", "black", "white", "warm", "cold"]
positions = ["beginning", "end", "middle"]
letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
           "w", "x", "y", "z"]


def get_instructions():
    color = colors[random.randrange(0, len(colors))]
    position = positions[random.randrange(0, len(positions))]
    letter = letters[random.randrange(0, len(letters))]
    instructions = """- Find a book with %s color in its cover. \n- Flip to the %s of the book. \n- Find a line that speaks to you that contains the letter %s. \n- Type `/wanderverse show` to see the last line of the poem, or `/wanderverse add [your line]` to add your line 
    """ % (color, position, letter)
    return instructions.strip()
