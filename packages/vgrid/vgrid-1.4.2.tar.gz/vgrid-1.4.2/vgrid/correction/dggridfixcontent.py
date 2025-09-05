import json
import re
import os
import argparse


def fix_content(input_file, output_file):
    with open(input_file, "r") as infile:
        content = infile.read()
    # Ensure all property names are in double quotes
    # content = re.sub(r'(\w+):', r'"\1":', content)
    # Ensure 'name' properties are wrapped in double quotes for values that are numbers or hexadecimal strings
    content = re.sub(r'("name":)([^\s,}]+)', r'\1"\2"', content)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error parsing corrected GeoJSON: {e}")
        return

    with open(output_file, "w") as outfile:
        json.dump(data, outfile, indent=2)

    print(f"GeoJSON has been fixed and saved to {output_file}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fix GeoJSON content from DGGRID")
    parser.add_argument("input", help="Input GeoJSON file")

    # Parse the arguments
    args = parser.parse_args()

    # Derive output filename by appending "_fixed" to the input filename
    # output_file = f"{args.input.rsplit('.', 1)[0]}_content_fixed.geojson"
    output_file = os.path.join(
        os.getcwd(),
        f"{os.path.splitext(os.path.basename(args.input))[0]}_content_fixed.geojson",
    )

    # Call the function with the input and output file
    fix_content(args.input, output_file)


if __name__ == "__main__":
    main()
