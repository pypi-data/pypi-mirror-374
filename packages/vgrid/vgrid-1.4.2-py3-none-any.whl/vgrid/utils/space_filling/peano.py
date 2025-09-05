import matplotlib.pyplot as plt

def peano_curve(order, x0=0, y0=0, size=1):
    """
    Recursively generate the Peano curve points.
    order: recursion depth
    (x0,y0): bottom-left corner of the current square
    size: size of the current square
    """
    if order == 0:
        return [(x0 + size/2, y0 + size/2)]

    pts = []
    step = size / 3

    # fixed snake visiting order in 3x3 grid
    pattern = [
        (0,0), (1,0), (2,0),
        (2,1), (1,1), (0,1),
        (0,2), (1,2), (2,2)
    ]

    for (i, j) in pattern:
        nx, ny = x0 + i*step, y0 + j*step
        pts.extend(peano_curve(order-1, nx, ny, step))

    return pts


def peano(order):
    """Generate and plot the Peano curve of a given order."""
    pts = peano_curve(order)
    xs, ys = zip(*pts)

    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, linewidth=0.6)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.axis("off")
    size = 3 ** order
    plt.title(f"Peano Space-Filling Curve — order {order} (grid {size}×{size})")
    plt.show()
    return pts, size

