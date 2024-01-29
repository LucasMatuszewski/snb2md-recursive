# Copyright (c) 2024 Lucas Matuszewski
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this file (originally named snb2txt) and associated documentation files 
# (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE. 

import argparse
import os
import subprocess

# Define the command-line arguments
parser = argparse.ArgumentParser(description="Recursively converts Samsung S-Note `.snb` files in provided `startdir` (or current directory) to `.md` files in markdown syntax and export them to `/exported` directory.")
parser.add_argument("-d", "--dir", dest="image_dir", help="Extract images to <image_dir>", metavar="<image_dir>")
parser.add_argument("-w", "--wikilink", dest="wikilink", action="store_true", help="If links and images should be [[WikiLinks]] instead of Markdown links (e.g. for Obsidian)")
parser.add_argument("startdir", nargs='?', default='.', help="Directory to start the recursive search for .snb files. If not provided, the current directory will be used.")
  
args = parser.parse_args()

# Define the recursive function
def process_directory(directory, args):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".snb"):
                # Get the full path of the .snb file
                full_path = os.path.join(root, file)
                
                # Get the relative path of the .snb file
                rel_path = os.path.relpath(full_path, directory)
                
                # Prepend the 'exported' directory to the output file path
                output_path = os.path.join('exported', rel_path)
                
                # Replace the .snb extension with .md
                output_path = output_path.rsplit('.', 1)[0] + '.md'

                # Create the necessary directories in the output path
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # # Set image_dir to the directory of the output .md file
                # image_dir = os.path.dirname(output_path)

                # Get the directory name from rel_path
                directory_name = os.path.dirname(rel_path)
                # Set image_dir to 'exported' joined with the directory name
                image_dir = os.path.join('exported', directory_name)

                # If args.image_dir is provided, append it to image_dir
                if args.image_dir is not None:
                    image_dir = os.path.join(image_dir, args.image_dir)

                command = ['python', 'snb2txt.py', full_path, '-o', output_path, '-d', image_dir]
                if args.wikilink:
                    command.extend(["-w"])
                
                # Call the snb2txt.py script to convert the .snb file to .md
                subprocess.call(command)

# Call the recursive function
process_directory(args.startdir or '.', args)