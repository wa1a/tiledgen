import json 
from enum import IntEnum


# right now one tileset is describet in a json file, 
# maybe we can describe ALL available tilesets in the same file?
# the tileset json files can be created via the tiled editor.
class Tileset():
    def __init__(self, tilesetfilename):
        with open(tilesetfilename,'r') as tilesetfile:
            self.content = json.load(tilesetfile)
    
    def getTileset(self,startid):
        return {"columns": self.content["columns"],
                "firstgid": startid,
                "image": self.content["image"],
                "imageheight": self.content["imageheight"],
                "imagewidth": self.content["imagewidth"],
                "margin": self.content["margin"],
                "name": self.content["name"],
                "spacing": self.content["spacing"],
                "tilecount": self.content["tilecount"],
                "tileheight": self.content["tileheight"],
                "tilewidth": self.content["tilewidth"]}




# a thing is something we can add to a room on a position
class Thing():
    def __init__(self, tileset_to_use: Tileset, tileID, x,y):
       self.tileset = tileset_to_use
       self.tileID = tileID
       self.x = x
       self.y = y

class Layer():
    def __init__(self, id, width, height,name):
        self.data = [0] * (width * height)
        self.height = height 
        self.id = id
        self.name = name
        self.opacity = 1
        self.type = "tilelayer"
        self.visible = True
        self.width  = width
        self.x = 0
        self.y = 0

class RoomData():
    
    def __init__(self, height, width):
        self.backgroundcolor = "#ffffffff"
        self.height=height 
        self.layers = []
        self.nextobjectid= 1
        self.orientation="orthogonal"
        self.properties= []
        self.renderorder="right-down"
        self.tileheight=32
        self.tilesets= []
        self.tilewidth=32
        self.version = 1
        self.tiledversion="1.0.3"
        self.width=height

class RoomLayers(IntEnum):
    BACKGROUND = 0
    THINGS = 1

class Room():
    def __init__(self,height, width):
        self.content=RoomData(height,width)
        self.content.layers.append(Layer(RoomLayers.BACKGROUND, self.content.width,self.content.height, "backgroundlayer")) # append layer for background
        self.content.layers.append(Layer(RoomLayers.THINGS, self.content.width,self.content.height, "thingslayer")) # append layer for things

    def _addTileset(self, tileset: Tileset):
         #check if the used tileset is allready added
        tilesetIsPresent = False
        for presentTileset in self.content.tilesets:
            if presentTileset["name"] == tileset.content["name"]:
                tilesetIsPresent = True
        if not tilesetIsPresent:
            self.content.tilesets.append(tileset.getTileset(1))

    def _addTileToLayer(self, layer, tileid,pos):
            self.content.layers[layer].data[pos] = tileid+1 #seems like tiled is using 0 based indexing but showing 1 based indexing in gui

    def setBackgroundColor(self,intvalue):
        self.content.backgroundcolor = "#%x" % intvalue 

    def setBackgroundTile(self, tileset: Tileset, tileid):
        self._addTileset(tileset) #maybe the tileset used for background is not present in room? Better try to add it 
        for pos in range(self.content.layers[RoomLayers.BACKGROUND].width * self.content.layers[RoomLayers.BACKGROUND].height):
            self._addTileToLayer(RoomLayers.BACKGROUND,tileid,pos) 
        
               
    def toJSON(self):
        #todo: remove empty layers (all data elements 0), otherweise tiled will not load the file (background may not be set)
        return json.dumps(self.content, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def toFile(self, file):
        with open(file,'w') as roomjsonfile:
            roomjsonfile.write(self.toJSON())

    def add(self, thingToAdd: Thing):
        self._addTileset(thingToAdd.tileset)
        # now add the tile to the layer
        posInData = (thingToAdd.y*self.content.width)+thingToAdd.x
        self._addTileToLayer(RoomLayers.THINGS,thingToAdd.tileID,posInData)







def main():
    print("tiled generator")

    mytileset = Tileset("testtileset.json") # load the tileset from description file
    
    # create room
    myroom = Room(5,5)
    myroom.setBackgroundColor(0x55aa55aa) #example how to change room background color
    myroom.setBackgroundTile(mytileset,660) #example how to add a tile as background layer filled with that tile

    # create a thing, here a castle :-) and add it to the room 
    castle = Thing(mytileset,586,0,0)
    myroom.add(castle)

    # second castle 
    castle2 = Thing(mytileset,586,3,2)
    myroom.add(castle2)


    # print and export the created room
    myroomjson = myroom.toJSON()
    print(myroomjson)
    myroom.toFile('room.json')

if __name__ == "__main__":
    main()


