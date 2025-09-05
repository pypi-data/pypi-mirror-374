import math
import matplotlib.pyplot as plt

def sierpinski_instructions(order):
    """L-system string for the Sierpinski arrowhead curve."""
    s = "A"
    rules = {"A": "B-A-B", "B": "A+B+A"}
    for _ in range(order):
        s = "".join(rules[ch] if ch in rules else ch for ch in s)
    return s

def sierpinski_points(order):
    """Interpret L-system into (x,y) points (turtle graphics)."""
    instr = sierpinski_instructions(order)
    angle = math.radians(60)
    x, y = 0.0, 0.0
    dx, dy = 1.0, 0.0     # initial heading = right
    pts = [(x, y)]
    for ch in instr:
        if ch in ("A", "B"):
            x += dx; y += dy
            pts.append((x, y))
        elif ch == "+":   # left 60°
            ndx = dx * math.cos(angle) - dy * math.sin(angle)
            ndy = dx * math.sin(angle) + dy * math.cos(angle)
            dx, dy = ndx, ndy
        elif ch == "-":   # right 60°
            ndx = dx * math.cos(-angle) - dy * math.sin(-angle)
            ndy = dx * math.sin(-angle) + dy * math.cos(-angle)
            dx, dy = ndx, ndy
    return pts

def sierpinski(order, grid_size=None, orient='tl', show=True):
    """
    Generate & plot Sierpinski arrowhead curve.
    - order: recursion depth
    - grid_size: scale target (if None, uses 2**order)
    - orient: 'tl','bl','tr','br' places/rotates the triangle
    - returns: (scaled_points, bbox)
    """
    pts = sierpinski_points(order)
    xs, ys = zip(*pts)
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    width = xmax - xmin
    height = ymax - ymin

    if grid_size is None:
        grid_size = 2 ** order

    # scale so largest span fits grid_size-1 (0..grid_size-1)
    span = max(width, height) or 1.0
    s = (grid_size - 1) / span
    tx = -xmin * s
    ty = -ymin * s
    scaled = [(x*s + tx, y*s + ty) for (x, y) in pts]

    # optional orientation (rotate/flip to match expected placement)
    if orient == 'tl':      # top-left: rotate and flip
        oriented = [(y, grid_size - 1 - x) for (x, y) in scaled]
    elif orient == 'bl':    # bottom-left (default orientation)
        oriented = scaled
    elif orient == 'tr':
        oriented = [(grid_size - 1 - x, y) for (x, y) in scaled]
    elif orient == 'br':
        oriented = [(grid_size - 1 - y, x) for (x, y) in scaled]
    else:
        oriented = scaled

    if show:
        xs2, ys2 = zip(*oriented)
        plt.figure(figsize=(6, 6))
        plt.plot(xs2, ys2, linewidth=0.9)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlim(-1, grid_size)
        plt.ylim(-1, grid_size)
        plt.xticks([]); plt.yticks([])
        plt.title(f"Sierpiński Arrowhead — order {order} (scaled to {grid_size}×{grid_size})")
        plt.show()

    return oriented, ((xmin, ymin), (xmax, ymax))

# Example: order=3, grid 8x8, top-left oriented
sierpinski(3, grid_size=8, orient='tl')
