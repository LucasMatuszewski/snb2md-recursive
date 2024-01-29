#!/usr/bin/python

# Copyright (c) 2024 Lucas Matuszewski - for below modifications:
# - support for Python 3
# - saving to file instead of `stdout`
# - extract images by default to the same folder
# - optional WikiLinks (for Obsidian)
# - recursive processing of all .snb files in the directory (separate `snb2md-recursive.py`)

# Copyright (c) 2013 Matthias S. Benkmann
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


from __future__ import with_statement, division, absolute_import, print_function

import codecs
import sys
import os
import zlib
from io import BytesIO
from PIL import Image
from zipfile import ZipFile
from xml.dom import minidom
import xml.dom
# from optparse import OptionParser, OptionGroup
import argparse
from unidecode import unidecode
import re

class Style(object):
  def __init__(self, bold, italic, underline):
    self.bold = bold
    self.italic = italic
    self.underline = underline


if __name__ == "__main__":
  try:
    # replace stderr and stdout with a utf-8 encoding StreamWriter, so that it can output non-ASCII characters
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
  except Exception as e:
    print(f"An error occurred: {e}")

  usage = "%(prog)s [-d <image_dir>] <infile.snb>"

  parser = argparse.ArgumentParser(usage=usage, description="Converts Samsung S-Note `.snb` file <infile.snb> to `.md` file in markdown syntax.")
  parser.add_argument("-d", "--dir", dest="image_dir", help="Extract images to <image_dir>", metavar="<image_dir>")
  parser.add_argument("-o", "--output", dest="outfile", help="Specify the output markdown file name. If not provided, the input file name with a .md extension will be used.", metavar="<outfile>")
  parser.add_argument("-w", "--wikilink", dest="wikilink", action="store_true", help="If links and images should be [[WikiLinks]] instead of Markdown links (e.g. for Obsidian)")
  parser.add_argument("infile", help="Samsung S-Note file <infile.snb> to convert to text in markdown syntax. The result is written to stdout so you can save it by adding ` > <output-file.md>` on the end of command.")
  options = parser.parse_args()
  if options.infile is None:
    parser.print_help()
    sys.exit(1)

  charStyle = {}
  rels = {}
  imgpath = ""
  include_backgrounds = False
  infile = options.infile

  # Get the relative path to the input file
  infile_path = os.path.dirname(os.path.relpath(infile))

  # If --dir is provided, use it as the image directory (relatively to the input file). Otherwise, use the relative path of the input file
  if options.image_dir is not None:
    imgpath = os.path.join(infile_path, options.image_dir)
  else:
    imgpath = infile_path
  
  zipfl = ZipFile(infile, "r")
  
  try:
    sty = zipfl.open("snote/styles.xml")
  except KeyError:
    sty = zipfl.open("/snote/styles.xml")
  styles = minidom.parseString(sty.read())
  for style in styles.getElementsByTagName("sn:style"):
    if style.getAttributeNode("sn:type").value == "character":
      charStyleId = style.getAttributeNode("sn:styleId").value
      charStyle[charStyleId] = Style(len(style.getElementsByTagName("sn:b"))>0, len(style.getElementsByTagName("sn:i"))>0, len(style.getElementsByTagName("sn:u"))>0)
  sty.close()
  
  try:
    rel = zipfl.open("snote/_rels/snote.xml.rels")
  except KeyError:
    rel = zipfl.open("/snote/_rels/snote.xml.rels")
  relations = minidom.parseString(rel.read())
  for relation in relations.getElementsByTagName("Relationship"):
    relId = relation.getAttribute("Id")
    target = relation.getAttribute("Target")
    rels[relId] = target
  rel.close()

  # Get the base name of the input file (without the extension)
  infilename = os.path.splitext(os.path.basename(options.infile))[0]
  
  # If --output is not provided, use the input file name with a .md extension as the default output file name
  if options.outfile is None:
    options.outfile = f"{infilename}.md"

  # Open the output file for writing (`with` will close the file automatically when done or on error)
  with open(options.outfile, 'w') as outfile:

    # Use file name as a header + add info that this is S-Note file
    outfile.write("\n## %s - %s \n\n" % (infilename, 'exported from S-Note'))
      
    try:
      notexml = zipfl.open("snote/snote.xml")
    except KeyError:
      notexml = zipfl.open("/snote/snote.xml")
    note = minidom.parseString(notexml.read())
    
    node = note.documentElement
    while True:
      if node.firstChild is not None:
        node = node.firstChild
      elif node.nextSibling is not None:
        node = node.nextSibling
      else:
        while True:
          node = node.parentNode
          if node.nodeType == xml.dom.Node.DOCUMENT_NODE: sys.exit(0)
          if node.nextSibling is None: continue
          node = node.nextSibling
          break
      
      if node.nodeType != xml.dom.Node.ELEMENT_NODE: continue
    
      block = node
      if block.tagName == "v:imagedata":
        is_background = block.parentNode.parentNode.parentNode.getAttribute("sn:insertimagetype") == "1"
        imgrelpath = rels[block.getAttribute("r:id")]
        imgname = infilename + "-" + imgrelpath.rsplit("/",1)[1]

        # convert to ASCII (to replace special characters like polish ą, ę, ł, etc.)
        imgname = unidecode(imgname)
        imgname = re.sub(r"[^\w\-\.]", "-", imgname) # replace non-alphanumeric in the image name with a dash "-"
        if include_backgrounds or not is_background:
          try:
            imgfile = zipfl.open("snote/"+imgrelpath)
          except KeyError:
            imgfile = zipfl.open("/snote/"+imgrelpath)
          imgdata = imgfile.read()
          imgfile.close()
          if imgname.endswith(".zdib"):
            imgdata = zlib.decompress(imgdata)
            imgname = imgname.rsplit(".",1)[0]+".png"
            width = imgdata[5] * 256 + imgdata[4]
            height = imgdata[9] * 256 + imgdata[8]
            imgdata = imgdata[52:]
            img = Image.frombytes("RGBA",(width,height),imgdata)
            bytesIo = BytesIO()
            img.save(bytesIo, "PNG")
            imgdata = bytesIo.getvalue()
            bytesIo.close()
          
          # Extract the image (create the directory if it doesn't exist)
          imgpath = os.path.join(options.image_dir, imgname)
          os.makedirs(os.path.dirname(imgpath), exist_ok=True)
          imgout = open(imgpath,"wb")
          imgout.write(imgdata)
          imgout.close()

          # Create the Markdown link TODO: temporary fix to remove the 'exported/{directory}' from the link. But will it work well for multiple nested directories?
          markdown_link = os.path.basename(options.image_dir)
          
          # Write the image link as a WikiLink or Markdown link
          if options.wikilink:
              outfile.write("\n![[%s]]\n\n" % (imgname))
          else:
              outfile.write("\n![%s](%s)\n\n" % (imgname, os.path.join(markdown_link, imgname)))
      
      if block.tagName == "sn:l":
        for run in block.getElementsByTagName("sn:r"):
          surround = ""
          if len(run.getElementsByTagName("sn:t")) > 0:
            charStyleId = "Character" + run.getAttributeNode("sn:rStyle").value
            if charStyle[charStyleId].bold: 
              surround = "**"
              outfile.write(surround)
            else:
              if charStyle[charStyleId].italic or charStyle[charStyleId].underline: 
                surround = "_"
                outfile.write(surround)
          
          for bullet in run.getElementsByTagName("sn:bulletText"):
            if bullet.firstChild.data == "l":
              outfile.write("* ")
            elif bullet.firstChild.data == "u":
              outfile.write("    - ")
            elif bullet.firstChild.data[0].isdigit():
              #outfile.write(bullet.firstChild.data)
              outfile.write("1. ")
            else:
              outfile.write("        + ")
          
          for text in run.getElementsByTagName("sn:t"):
            for t in text.childNodes:
              if t.nodeType == xml.dom.Node.TEXT_NODE:
                outfile.write(t.data)
          
          outfile.write(surround)

          if len(run.getElementsByTagName("sn:paraend"))+len(run.getElementsByTagName("sn:br")) > 0:
            outfile.write("\n")
        outfile.write("\n")
      
else:
  print("This is a module. Use it from the command line.")
  sys.exit(1)