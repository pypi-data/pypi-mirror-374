# Retry: Morton curve on global Mollweide map with smaller default order (6 -> 64x64 = 4096 points)
import math
import matplotlib.pyplot as plt
import geopandas as gpd

def deinterleave_bits(n: int):
    x = 0
    y = 0
    bit = 0
    while n:
        x |= (n & 1) << bit
        n >>= 1
        y |= (n & 1) << bit
        n >>= 1
        bit += 1
    return x, y

def morton_coords(order: int):
    size = 1 << order
    n_points = size * size
    coords = [deinterleave_bits(i) for i in range(n_points)]
    return coords, size

def webmercator_y_to_lat(y_norm):
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y_norm))))

def morton_to_lonlat(order):
    coords, size = morton_coords(order)
    lonlat = []
    for x, y in coords:
        x_norm = x / size
        y_norm = y / size
        lon = x_norm * 360.0 - 180.0
        lat = webmercator_y_to_lat(y_norm)
        lonlat.append((lon, lat))
    return lonlat

def morton(order, projection='mollweide'):
    """
    Generate and plot Morton (Z-order) curve.
    
    Args:
        order: Resolution order (e.g., 6 for 64x64 grid)
        projection: Map projection ('mollweide' or 'moll')
    """
    pts = morton_to_lonlat(order)
    
    lons = [math.radians(((lon + 180) % 360) - 180) for lon, lat in pts]
    lats = [math.radians(lat) for lon, lat in pts]
    
    fig = plt.figure(figsize=(12,6))
    ax = fig.add_subplot(111, projection=projection)
    ax.plot(lons, lats, linewidth=0.6)
    ax.grid(True, linestyle=':', linewidth=0.5)
    ax.set_title(f"Morton (Z-order) Curve on a Global Mollweide Map — order={order} (grid={1<<order}×{1<<order})")
    ax.scatter([lons[0]], [lats[0]], marker='o', s=30)
    ax.scatter([lons[-1]], [lats[-1]], marker='x', s=30)
    
    plt.tight_layout()
    out_path = f"morton_global_order{order}.png"
    # plt.savefig(out_path, dpi=200)
    plt.show()

def morton_cli():
    """
    Command-line interface for Morton curve generation and visualization.
    
    Usage examples:
        python morton.py --order 6 --projection mollweide
        python morton.py --order 8 --projection moll
        python morton.py --order 7
    """
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="Generate and visualize Morton (Z-order) curves",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python morton.py --order 6                    # Generate order 6 curve with default mollweide projection
  python morton.py --order 8 --projection moll  # Generate order 8 curve with moll projection
  python morton.py --order 7                    # Generate order 7 curve with default projection
  python morton.py --help                       # Show this help message
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
        help='Map projection to use (default: mollweide)'
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
        print(f"Generating Morton curve for order {args.order} with {args.projection} projection...")
        morton(args.order, args.projection)
        print("Morton curve generation completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run CLI if script is executed directly
    morton_cli()