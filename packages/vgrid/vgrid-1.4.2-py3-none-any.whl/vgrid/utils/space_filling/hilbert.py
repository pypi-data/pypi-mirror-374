import matplotlib.pyplot as plt
import math

def hilbert_index_to_xy(index, order):
    """Convert Hilbert index to (x, y)."""
    x = y = 0
    n = 1 << order
    idx = index
    s = 1
    while s < n:
        rx = 1 & (idx // 2)
        ry = 1 & (idx ^ rx)
        if ry == 0:
            if rx == 1:
                x, y = s - 1 - x, s - 1 - y
            x, y = y, x
        x += s * rx
        y += s * ry
        idx //= 4
        s *= 2
    return x, y


def hilbert(order):
    """Plot the 2D Hilbert curve for a given order."""
    n_points = 1 << (2 * order)
    pts = [hilbert_index_to_xy(i, order) for i in range(n_points)]
    size = 1 << order

    xs, ys = zip(*pts)
    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, linewidth=0.6)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlim(-1, size)
    plt.ylim(-1, size)
    plt.xticks([])
    plt.yticks([])
    plt.title(f"Hilbert Space-Filling Curve — order {order} (grid {size}×{size})")
    plt.show()


def webmercator_y_to_lat(y_norm):
    """Convert normalized Web Mercator Y coordinate to latitude."""
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y_norm))))


def hilbert_to_lonlat(order):
    """Convert Hilbert curve coordinates to longitude/latitude pairs."""
    coords, size = hilbert_coords(order)
    lonlat = []
    for x, y in coords:
        x_norm = x / size
        y_norm = y / size
        lon = x_norm * 360.0 - 180.0
        lat = webmercator_y_to_lat(y_norm)
        lonlat.append((lon, lat))
    return lonlat


def hilbert_coords(order):
    """Generate Hilbert curve coordinates for a given order."""
    n_points = 1 << (2 * order)
    coords = [hilbert_index_to_xy(i, order) for i in range(n_points)]
    size = 1 << order
    return coords, size


def hilbert_mollweide(order, projection='mollweide'):
    """
    Generate and plot Hilbert curve on a global Mollweide map.
    
    Args:
        order: Resolution order (e.g., 6 for 64x64 grid)
        projection: Map projection ('mollweide' or 'moll')
    """
    pts = hilbert_to_lonlat(order)
    
    lons = [math.radians(((lon + 180) % 360) - 180) for lon, lat in pts]
    lats = [math.radians(lat) for lon, lat in pts]
    
    fig = plt.figure(figsize=(12,6))
    ax = fig.add_subplot(111, projection=projection)
    ax.plot(lons, lats, linewidth=0.6)
    ax.grid(True, linestyle=':', linewidth=0.5)
    ax.set_title(f"Hilbert Space-Filling Curve on a Global Mollweide Map — order={order} (grid={1<<order}×{1<<order})")
    ax.scatter([lons[0]], [lats[0]], marker='o', s=30, label='Start')
    ax.scatter([lons[-1]], [lats[-1]], marker='x', s=30, label='End')
    ax.legend()
    
    plt.tight_layout()
    out_path = f"hilbert_global_order{order}.png"
    # plt.savefig(out_path, dpi=200)
    plt.show()


def hilbert_cli():
    """
    Command-line interface for Hilbert curve generation and visualization.
    
    Usage examples:
        python hilbert.py --order 6 --projection mollweide
        python hilbert.py --order 8 --projection moll
        python hilbert.py --order 7
        python hilbert.py --mollweide --order 6
    """
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="Generate and visualize Hilbert space-filling curves",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hilbert.py --order 6                    # Generate order 6 curve (2D view)
  python hilbert.py --mollweide --order 6        # Generate order 6 curve on Mollweide projection
  python hilbert.py --order 8 --projection moll  # Generate order 8 curve with moll projection
  python hilbert.py --help                       # Show this help message
        """
    )
    
    parser.add_argument(
        '--order', '-o',
        type=int,
        default=6,
        help='Resolution order (default: 6, creates 64x64 grid)'
    )
    
    parser.add_argument(
        '--projection', '-p',
        choices=['mollweide', 'moll'],
        default='mollweide',
        help='Map projection to use for mollweide view (default: mollweide)'
    )
    
    parser.add_argument(
        '--mollweide', '-m',
        action='store_true',
        help='Generate Hilbert curve on Mollweide projection instead of 2D view'
    )
    
    args = parser.parse_args()
    
    # Validate order
    if args.order < 1 or args.order > 12:
        print(f"Warning: Order {args.order} may create very large grids. Consider using order <= 10 for reasonable performance.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    try:
        if args.mollweide:
            print(f"Generating Hilbert curve for order {args.order} with {args.projection} projection...")
            hilbert_mollweide(args.order, args.projection)
            print("Hilbert curve generation on Mollweide projection completed successfully!")
        else:
            print(f"Generating Hilbert curve for order {args.order} (2D view)...")
            hilbert(args.order)
            print("Hilbert curve generation completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run CLI if script is executed directly
    hilbert_cli()
