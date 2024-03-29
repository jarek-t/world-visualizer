import os, sys, re, json, imageio
from progress.bar import FillingSquaresBar
from PIL import Image, ImageDraw, ImageFont

# - # - # - # - # - # - # - # - # - #
# Takes a text file's location and returns an image
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

  # Could be removed/replaced with config/defaults/initializers >>
  colors = {
    "prim": (137, 176, 63),
    "title": (83, 79, 83)
  }

  fonts = {
    "prim": ImageFont.truetype(os.path.abspath('.') + "/bin/fonts/Roboto-Bold.ttf", size=55),
    "title": ImageFont.truetype(os.path.abspath('.') + "/bin/fonts/Roboto-Medium.ttf", size=150),
    "title2": ImageFont.truetype(os.path.abspath('.') + "/bin/fonts/Roboto-Bold.ttf", size=125)
  }
  # <<

  def convert(self, source):
    background = Image.open(self.backgroundURI)
    write = ImageDraw.Draw(background)
    self.ready(source)
    
    count = 0
    for line in self.source: 
      yPos = self.titleY + 60 * count

      # print(yPos) # debug text positioning
      location = (50, yPos)

      write.text(location, line, font=self.fonts["prim"], fill=self.colors["prim"])

      count += 1

    return background

  def ready(self, source):
    # Get rid of \n since our source in in a list
    self.source = [line[0:-1] for line in source]

    self.sourceLength = len(self.source)

  def getResult(self): return self.out

  # Please don't construct hundreds of covert instances per gif
  def setSource(self, newSource): self.source = newSource

  def __init__(self, styles = False):
    # Maybe look into PIL's image creation instead of relying on a pregenerated background (make config options?)
    self.backgroundURI = "bg.png" if not isinstance(styles, dict) or "bg" not in styles else styles["bg"]    

    # This ternary shouldn't be necessary with BatchTextVisualizer defaults in place
    self.titleY = (Image.open(self.backgroundURI)).size[1] * (10 if not isinstance(styles, dict) or "titleFootprint" not in styles else styles["titleFootprint"])/100
    
    for s in ["colors", "fonts"]:
      # Also should be able to be reduced with BTV defaults
      if isinstance(styles, dict) and isinstance(styles[s], dict) and s in styles:
        target = self.colors if s == "colors" else self.fonts

        for key in styles[s]:
          target[key] = (styles[s])[key]

# - # - # - # - # - # - # - # - # - #
# Finds all text files (to-be-frames), handles configuration, outputs .gif
# - # - # - # - # - # - # - # - # - #

class BatchTextVisualizer:
  targets = []
  converted = []
  out = False 
  timePerFrame = False

  writer = TextVisualizer()

  def outOfRange(self, index): 
    return index < 0 or index > len(self.targets)

  # Parse a directory and find all frame-conversion candidates
  def getTargets(self, dn = False):
    fileNames = [dn + "/" + fn for fn in os.listdir(dn)]

    sort = lambda fileName: int((re.findall(r'\d+', fileName))[0])
    fileNames.sort(key = sort)

    return fileNames

  # Convert a single text file to a frame (has ability to place in final gif non-sequentially)
  # Non-sequential placement not currently used
  def convertTarget(self, target, order = False):
      result = self.writer.convert(target)
      
      if order and not self.outOfRange(order):
        self.converted.insert(order, result)

      return result

  # Converts a range of the source (exports at same time, this should be fixed)
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

  # Export each frame as a still image
  def export(self):
    count = 0

    for img in self.converted:
      img.save("out/"+(str(count) + ".png"))

      count += 1
  
  def __init__(self, config = False):
    finalArgs = {}
    userArgs = False
    defaultArgs = json.load(open('bin/visualizerDefaults.json'))

    # Load the config file if valid filename is given 
    if isinstance(config, str) and config.endswith('.json'):
      absPath = os.path.abspath('.') + "/" + config if config[0] != "/" else os.path.abspath('.') + config

      fileName = open(absPath) if os.path.exists(absPath) else open(config) if os.path.exists(config) else False
      
      if fileName: userArgs = json.load(fileName)
    
    # Favor client provided configuration while building
    if userArgs:
      for arg, value in defaultArgs.items():
        finalArgs[arg] = userArgs[arg] if arg in userArgs else value

    else:
      print('No config given, continuing with defaults...')
      finalArgs = defaultArgs

    self.targets = self.getTargets(finalArgs['srcDir'])
    print("\nFound " + str(len(self.targets)) + " text files to animate.\n")

    self.convertAll()

    self.export()
  
# - # - # - # - # - # - # - # - # - #

batch = BatchTextVisualizer()