import json 
from enum import IntEnum
from enum import Enum


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





class LayerTypes(Enum):
    TILELAYER=0
    OBJECTGROUP=1

class Layer():
    def __init__(self,type: LayerTypes, id,x,y, width, height,name):
        if type == LayerTypes.TILELAYER:
            self.data = [0] * (width * height)
            self.type = "tilelayer"
        if type == LayerTypes.OBJECTGROUP:
            self.objects = []
            self.type = "objectgroup"
        self.height = height 
        self.id = id
        self.name = name
        self.opacity = 1
        self.visible = True
        self.width  = width
        self.x = x
        self.y = y

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
    OBJECTS = 2

class Room():
    def __init__(self,height, width):
        self.content=RoomData(height,width)
        self.content.layers.append(Layer(LayerTypes.TILELAYER,RoomLayers.BACKGROUND,0,0, self.content.width,self.content.height, "start")) # makes the entry to tha map random. See https://workadventu.re/create-map.html TODO provide an explicit start point
        self.content.layers.append(Layer(LayerTypes.TILELAYER,RoomLayers.THINGS, 0,0,self.content.width,self.content.height, "thingslayer")) # append layer for things
        self.content.layers.append(Layer(LayerTypes.OBJECTGROUP,RoomLayers.OBJECTS, 0,0,self.content.width,self.content.height, "floorLayer")) # append layer for drawing the players

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
        
               
    def __str__(self):
        #todo: remove empty layers (all data elements 0), otherweise tiled will not load the file (background may not be set)
        return json.dumps(self.content, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def toFile(self, file):
        with open(file,'w') as roomjsonfile:
            roomjsonfile.write(self.__str__())



# a thing is something we can add to a room on a position
class Thing():
    def __init__(self, tileset_to_use: Tileset, tileID, x,y):
       self.tileset = tileset_to_use
       self.tileID = tileID
       self.x = x
       self.y = y
    def addToRoom(self, room: Room):
        room._addTileset(self.tileset)
        # now add the tile to the layer
        posInData = (self.y*room.content.width)+self.x
        room._addTileToLayer(RoomLayers.THINGS,self.tileID,posInData)





def main():
    print("tiled generator")

    mytileset = Tileset("testtileset.json") # load the tileset from description file
    
    # create room
    myroom = Room(5,5)
    myroom.setBackgroundColor(0x55aa55aa) #example how to change room background color
    myroom.setBackgroundTile(mytileset,660) #example how to add a tile as background layer filled with that tile

    # create a thing, here a castle :-) and add it to the room 
    castle = Thing(mytileset,586,0,0)
    castle.addToRoom(myroom)

    # second castle 
    castle2 = Thing(mytileset,586,3,2)
    castle2.addToRoom(myroom)


    # print and export the created room
    print(myroom)
    myroom.toFile('map.json')

if __name__ == "__main__":
    main()


