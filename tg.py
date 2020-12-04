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
    def __init__(self, width, height,name):
        self.data = [0] * (width * height)
        self.height = 4
        self.id = 2
        self.name = name
        self.opacity = 1
        self.type = "tilelayer"
        self.visible = True
        self.width  = 4
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
        self.content.layers.append(Layer(self.content.width,self.content.height, "backgroundlayer")) # append layer for background
        self.content.layers.append(Layer(self.content.width,self.content.height, "thingslayer")) # append layer for things


    def setBackground(self,intvalue):
        self.content.backgroundcolor = "#%x" % intvalue 

       
    def toJSON(self):
        return json.dumps(self.content, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def toFile(self, file):
        with open(file,'w') as roomjsonfile:
            roomjsonfile.write(self.toJSON())

    def add(self, thingToAdd: Thing):
        #check if the used tileset is allready added
        tilesetIsPresent = False
        for presentTileset in self.content.tilesets:
            if presentTileset["name"] == thingToAdd.tileset.content["name"]:
                tilesetIsPresent = True
                print("tileset is allready present")
        if not tilesetIsPresent:
            self.content.tilesets.append(thingToAdd.tileset.getTileset(1))
        # now add the tile to the layer
        posInData = (thingToAdd.y*self.content.width)+thingToAdd.x
        self.content.layers[RoomLayers.THINGS].data[posInData]=thingToAdd.tileID







def main():
    print("tiled generator")

    mytileset = Tileset("testtileset.json") # load the tileset from description file
    
    # create room
    myroom = Room(5,5)
    myroom.setBackground(0x55aa55aa) #example how to change room background color

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


