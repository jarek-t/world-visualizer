import os, sys, re

import imageio

from progress.bar import FillingSquaresBar

from PIL import Image, ImageDraw, ImageFont
# - # - # - # - # - # - # - # - # - #

class TextVisualizer:
  sourceLength = False
  totalY = False
  titleY = False

  source = False
  out = False

  backgroundURI = False
  background = False
  write = False

  colors = {
    "prim": (137, 176, 63),
    "title": (83, 79, 83)
  }
  fonts = {
    "prim": ImageFont.truetype(os.path.abspath('.') + "/fonts/Roboto-Bold.ttf", size=55),
    "title": ImageFont.truetype(os.path.abspath('.') + "/fonts/Roboto-Medium.ttf", size=150),
    "title2": ImageFont.truetype(os.path.abspath('.') + "/fonts/Roboto-Bold.ttf", size=125)
  }

  def convert(self, source):
    background = Image.open(self.backgroundURI)
    write = ImageDraw.Draw(background)
    self.ready(source)
    
    count = 0
    for line in self.source: 
      yPos = self.titleY + 60 * count

      # print(yPos)
      location = (50, yPos)

      write.text(location, line, font=self.fonts["prim"], fill=self.colors["prim"])

      count += 1

    return background

  def ready(self, source):
    self.source = [line[0:-1] for line in source]

    self.sourceLength = len(self.source)

  def getResult(self): return self.out

  def setSource(self, newSource): self.source = newSource

  def __init__(self, styles = False):
    self.backgroundURI = "bg.png" if not isinstance(styles, dict) or "bg" not in styles else styles["bg"]    

    self.titleY = (Image.open(self.backgroundURI)).size[1] * (10 if not isinstance(styles, dict) or "titleFootprint" not in styles else styles["titleFootprint"])/100
    
    for s in ["colors", "fonts"]:
      if isinstance(styles, dict) and isinstance(styles[s], dict) and s in styles:
        target = self.colors if s == "colors" else self.fonts

        for key in styles[s]:
          target[key] = (styles[s])[key]

# - # - # - # - # - # - # - # - # - #

class BatchTextVisualizer:
  targets = []
  converted = []
  out = False 

  writer = TextVisualizer()

  def outOfRange(self, index): 
    return index < 0 or index > len(self.targets)

  def getTargets(self, dn = False):
    if not dn: return False

    fileNames = [dn   + "/"+fn for fn in os.listdir(dn)]

    sort = lambda fileName: int((re.findall(r'\d+', fileName))[0])
    fileNames.sort(key = sort)

    return fileNames

  def convertTarget(self, target, order = False):
    with open(target, "r") as source:
      result = self.writer.convert(source.readlines())
      
      if order and not self.outOfRange(order):
        self.converted.insert(order, result)

      source.close()

      return result
  
  def convertRange(self, start, end):
    if not len(self.targets):
      raise ValueError("There seem to be no targets...")
    elif self.outOfRange(start) or self.outOfRange(end):
      raise ValueError("Range does not exist.")

    progress = FillingSquaresBar('Converting', max = (end - start))
    for t in range(start, end): 
      
      img = self.convertTarget(self.targets[t])
      imgName = './out/'+str(t)+'.png' 
      img.save(imgName)

      img.close()

      progress.next()
    progress.finish()

    images = []
    for fn in os.listdir('out'):
      images.append(imageio.imread('out/'+fn))

    imageio.mimsave('out.gif', images, 'GIF-FI', duration = .25)

  def convertAll(self): self.convertRange(0, len(self.targets))

  def export(self):
    count = 0

    for img in self.converted:
      img.save("out/"+(str(count) + ".png"))

      count += 1
  
  def __init__(self, inDir, outTarget = False, bgFP = "bg.png"):
    self.targets = self.getTargets(inDir)
    print("\nFound " + str(len(self.targets)) + " text files to animate.\n")

    self.convertAll()

    self.export()
  
# - # - # - # - # - # - # - # - # - #

batch = BatchTextVisualizer('data')