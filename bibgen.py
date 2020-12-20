import urllib.request, json 
import random

class MAP():
    Layers = "layers"
    Width = "width"
    Height = "height"

class CONTENT():
    tileid = "tileid"
    title = "title"
    url ="url"
    x = "x"
    y = "y"

class LAYER():
    name = "name"
    data = "data"

class MapProperties():
    @staticmethod
    def load(map):
        MapProperties.height =  map[MAP.Layers][0][MAP.Height]
        MapProperties.width =  map[MAP.Layers][0][MAP.Width]
        MapProperties.map = map
    width = 0
    height = 0

class Position():
    def __init__ (self,x,y):
        self.x = x
        self.y = y

    def isValid(self):
        if self.x >= 0 and self.y >=0:
            return True
        return False

    @staticmethod
    def toDataIndex(position, roomWidth):
        return (position.y*roomWidth)+position.x
    @staticmethod
    def toPosition(dataIndex, roomWidth):
        y = dataIndex // roomWidth
        x = dataIndex - (roomWidth * y)
        return Position(x,y)



def getNextPosition():
    x = random.randint(0,MapProperties.width-1)
    y = random.randint(0,MapProperties.height-1)
    return Position(x,y)



#checks if one of the surrounding fields is accessable for a avatar
def checkNeighbourhood(map,layer,dataPos,tilesOfBookShelves):
    position = Position.toPosition(dataPos,MapProperties.width)
    tmap = [[0,1],[0,-1],[1,0],[-1,0]]
    for xy in tmap:
        newPosition= Position(position.x+xy[0],position.y+xy[1])

        if newPosition.isValid():
            posD = Position.toDataIndex(newPosition,MapProperties.width)
            if len(layer[LAYER.data]) > posD:
                tile = layer[LAYER.data][posD]
                if not tile in tilesOfBookShelves:
                    #Found accessable tile in neghbourhood
                    return True

    return False        


def getPossibleLocations(map,layerWithBooksName, tilesOfBookShelves):
    # find corresponding layer
    possibleLocation = []
    for layer in map[MAP.Layers]:
        if layer[LAYER.name] == layerWithBooksName:
            layerWithBooks = layer
            break
    #go trough all bookshelf tiles
    for dataPos in range(len(layerWithBooks[LAYER.data])):
        tileidOnLayer = layerWithBooks[LAYER.data][dataPos]
        if tileidOnLayer in tilesOfBookShelves:
            if checkNeighbourhood(map,layerWithBooks,dataPos,tilesOfBookShelves):
                possibleLocation.append(dataPos)
    return possibleLocation
    
    
     
def main():
    #constants, (TODO grab them from args?)
    MAX_BOOKS_ON_FLOOR = 20 #TODO check if number is useable, adapt if needed
    FILENAME_CONTENT_DEFINTION = "exampleContentDef.json"
    RANDOM_SEED = 2342001 #seed to make the "random" numbers predictable
    LAYER_NAME_BOOKS = "Floor"
    TILES_OF_BOOKSHELVES = [48,49,50,51,52,53,54,
                            64,65,66,67,68,69,70,
                            80,81,82,83,
                            96,97,98,99,
                            112,113,114,115,
                            128,129,130,131,
                            144,145,146,147,
                            160,161,162,163,
                            167,168,169,170]
    #init random
    random.seed(RANDOM_SEED) #TODO reinitalize on map change

    # load base map
    with urllib.request.urlopen("https://raw.githubusercontent.com/cccs/rc3-swabian-embassy/master/bib-og.json") as url:
        mapData = json.loads(url.read().decode())

    #load content definition 
    with open(FILENAME_CONTENT_DEFINTION) as json_file:
        content_definiton = json.load(json_file)

    currentMap = mapData # current map, because we want to change maps when max book limit is reached
    MapProperties.load(currentMap)
    possibleLocations = getPossibleLocations(currentMap, LAYER_NAME_BOOKS,TILES_OF_BOOKSHELVES)

    #we have to place every content
    for content in content_definiton:
        position = getNextPosition() #TODO rework, first generate list with possible valid locations, then choose randomly on of these
        print ("processing " + content[CONTENT.title]+" on pos x="+str(position.x)+" y:"+str(position.y))
        content["x"] = position.x
        content["y"] = position.y

    
    
    output = json.dumps(content_definiton, default=lambda o: o.__dict__, 
            sort_keys=True, indent=2)
    print(output)






if __name__ == "__main__":
    main()