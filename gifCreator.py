import text_to_image, os, sys, re

sort = lambda fileName: int((re.findall(r'\d+', fileName))[0])
fileNames = [fn for fn in os.listdir('data')]
fileNames.sort(key = sort)
#def getFileNames(dir):
  #   print(fileNames.sort())
   # for filename in os.listdir(dir):
        
    #    print(filename)
#for i in range(400):
#  title = "time_stamp" + str(i) + ".txt"
#  title2 = "image" + str(i) + ".png"
#  junk = text_to_image.encode(title, title2)
print(fileNames)
#getFileNames('data')
