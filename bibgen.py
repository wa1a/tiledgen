import urllib.request, json 
import random
from enum import Enum

class MAP():
    Layers = "layers"
    Width = "width"
    Height = "height"
    Tilesets = "tilesets"

class CONTENT():
    tileid = "tileid"
    title = "title"
    url ="url"
    x = "x"
    y = "y"

class LAYER():
    name = "name"
    data = "data"

class LayerTypes(Enum):
    TILELAYER=0
    OBJECTGROUP=1

class Layer():
    layerid = 0
    @staticmethod
    def getNextLayerId():
        Layer.layerid=Layer.layerid+1
        return Layer.layerid

    @staticmethod
    def getLayerListPosByName(layerList,name):
        for pos,element in enumerate(layerList):
            if element.name == name:
                return pos

    def __init__(self,type: LayerTypes, width, height,name):
        if type == LayerTypes.TILELAYER:
            self.data = [0] * (width * height)
            self.type = "tilelayer"
            self.properties =  []
        if type == LayerTypes.OBJECTGROUP:
            self.objects = []
            self.type = "objectgroup"
        self.height = height 
        self.id = Layer.getNextLayerId() 
        self.name = name
        self.opacity = 1
        self.visible = True
        self.width  = width
        self.x = 0 # tiled doku says this is always zero
        self.y = 0 # tiled doku says this is always zero

class LayerProperty():
    
    def __init__(self,name,ptype,value):
        self.name = name
        self.type = ptype
        self.value = value


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

class TILESET:
    firstgid = "firstgid"
    tilecount = "tilecount"
    tiles = "tiles"

class TILE:
    id = "id"
    properties = "properties"

class TILE_PROPERTY:
    name = "name"
    Type ="type"
    value = "value"

def isTileColliding(map,tileId):
    # find the tileset responsible for the tileid
    for tileset in map[MAP.Tilesets]:
        if tileId in range(tileset[TILESET.firstgid],tileset[TILESET.firstgid]+tileset[TILESET.tilecount]):
            # we found the tileset our tileid belongs to
            # now calc the tileid in the tileset
            innerTileId = tileId - (tileset[TILESET.firstgid]-1)
            for tile in tileset[TILESET.tiles]:
                if tile[TILE.id]== innerTileId:
                    #we found a tile description
                    for tileProperty in tile[TILE.properties]:
                        if (tileProperty[TILE_PROPERTY.name] == "collides") and (tileProperty[TILE_PROPERTY.value]== True):
                            #tile is colliding
                            return True
            return False
    return False #just to be shure...    





#checks if one of the surrounding fields is accessable for a avatar
def checkNeighbourhood(map,layer,dataPos,floorTile):
    position = Position.toPosition(dataPos,MapProperties.width)
    tmap = [[0,1],[0,-1],[1,0],[-1,0]]
    valids = []
    for xy in tmap:
        newPosition= Position(position.x+xy[0],position.y+xy[1])

        if newPosition.isValid():
            posD = Position.toDataIndex(newPosition,MapProperties.width)
            if len(layer[LAYER.data]) > posD:
                tile = layer[LAYER.data][posD]-1
                if not isTileColliding(map,tile): #TODO check for collisions with other links!
                    #Found accessable tile in neghbourhood
                    valids.append(posD)

    return valids        


def getPossibleLocations(map,layerWithBooksName, tilesOfBookShelves,floorTile):
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
            valids = checkNeighbourhood(map,layerWithBooks,dataPos,floorTile)
            if len(valids) > 0:
                possibleLocation.append([dataPos,valids])
    return possibleLocation
    
    
     
def main():
    #constants, (TODO grab them from args?)
    FILE_MAP_OUTPUT="map.json"
    MAX_BOOKS_ON_FLOOR = 20 #TODO check if number is useable, adapt if needed
    FILENAME_CONTENT_DEFINTION = "exampleContentDef.json"
    RANDOM_SEED = 2342001 #seed to make the "random" numbers predictable
    TILE_ID_FLOOR = 23
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
    possibleLocations = getPossibleLocations(currentMap, LAYER_NAME_BOOKS,TILES_OF_BOOKSHELVES,TILE_ID_FLOOR)
    locationsUsed=[]
    #we have to place every content
    for content in content_definiton:
        locationNotFound = True
        while locationNotFound:
            location = random.randint(0,len(possibleLocations)-1)
            if not location in locationsUsed:
                break
        #new layer, because the layer has the link info
        newLayer = Layer(LayerTypes.TILELAYER,MapProperties.width,MapProperties.height,content[CONTENT.title])
        newLayer.properties.append(LayerProperty("openWebsite", "string", content[CONTENT.url])) 

        #set a tile on the position to show the book
        newPosD = possibleLocations[location][0]
        newLayer.data[newPosD] = content[CONTENT.tileid]+1

        #add floortiles for accessing the link
        for newFloorTilePosD in possibleLocations[location][1]:
            newLayer.data[newFloorTilePosD] = TILE_ID_FLOOR+1

        #add the layer to the map
        currentMap[MAP.Layers].insert(len(currentMap[MAP.Layers])-1,newLayer)


        position = Position.toPosition(newPosD,MapProperties.width)
        print ("processing " + content[CONTENT.title]+" on data="+str(newPosD)+" pos x="+str(position.x)+" y:"+str(position.y))
        content["x"] = position.x
        content["y"] = position.y

    #save the map     
    mapOutput = json.dumps(currentMap, default=lambda o: o.__dict__, 
            sort_keys=True, indent=2)
    with open(FILE_MAP_OUTPUT,'w') as roomjsonfile:
        roomjsonfile.write(mapOutput)

    #save the content definition with position information
    output = json.dumps(content_definiton, default=lambda o: o.__dict__, 
            sort_keys=True, indent=2)
    print(output)






if __name__ == "__main__":
    main()