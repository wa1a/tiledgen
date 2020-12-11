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
                "tilewidth": self.content["tilewidth"],
                "tiles": []}





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

    def __init__(self,type: LayerTypes,x,y, width, height,name):
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
        self.startx = x
        self.starty = y
        self.x = 0 # tiled doku says this is always zero
        self.y = 0 # tiled doku says this is always zero

class LayerProperty():
    
    def __init__(self,name,ptype,value):
        self.name = name
        self.type = ptype
        self.value = value


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

class RoomLayers():
    BACKGROUND = "background" 
    THINGS = "thingslayer"
    FLOOR = "floorlayer"  
    START = "start"

class Room():
    def __init__(self,height, width):
        self.content=RoomData(height,width)
        self.content.layers.append(Layer(LayerTypes.TILELAYER,0,0, self.content.width,self.content.height, RoomLayers.BACKGROUND)) # layer to fill with tiles for background
        self.content.layers.append(Layer(LayerTypes.TILELAYER,0,0,self.content.width,self.content.height, RoomLayers.THINGS)) # append layer for things
        self.content.layers.append(Layer(LayerTypes.OBJECTGROUP,0,0,self.content.width,self.content.height, RoomLayers.FLOOR)) # append layer for drawing the players
    def _addTileset(self, tileset: Tileset):
         #check if the used tileset is allready added
        firstgid = 1
        tilesetIsPresent = False
        for presentTileset in self.content.tilesets:
            if presentTileset["firstgid"] == firstgid:
                firstgid = firstgid + presentTileset["tilecount"]
            if presentTileset["name"] == tileset.content["name"]:
                tilesetIsPresent = True
        if not tilesetIsPresent:
            tileset.content["firstgid"]= firstgid
            self.content.tilesets.append(tileset.content)

    def _getFirstGidOfTileset(self, tileset: Tileset):
        for aktTileset in self.content.tilesets:
            if aktTileset["name"] == tileset.content["name"]:
                return aktTileset["firstgid"]
        return 0

    def _addTileToLayer(self, layer_name, tileset: Tileset, tileid,pos):
        firstGid = self._getFirstGidOfTileset(tileset)
        layerPosition = Layer.getLayerListPosByName(self.content.layers,layer_name)
        self.content.layers[layerPosition].data[pos] = tileid + firstGid

   
    def setBackgroundColor(self,intvalue):
        self.content.backgroundcolor = "#%x" % intvalue 

    def setBackgroundTile(self, tileset: Tileset, tileid):
        self._addTileset(tileset) #maybe the tileset used for background is not present in room? Better try to add it 
        for pos in range(self.content.width * self.content.height):
            self._addTileToLayer(RoomLayers.BACKGROUND,tileset, tileid,pos) 
    
    
    
    def keepFloorLayerOnTop(self):
        indexOfFloorLayer = Layer.getLayerListPosByName(self.content.layers,RoomLayers.FLOOR)
        self.content.layers.append(self.content.layers[indexOfFloorLayer])
        self.content.layers.pop(indexOfFloorLayer)

    def __str__(self):
        #todo: remove empty layers (all data elements 0), otherweise tiled will not load the file (background may not be set)
        return json.dumps(self.content, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def toFile(self, file):
        with open(file,'w') as roomjsonfile:
            roomjsonfile.write(self.__str__())



# a thing is something we can add to a room on a position
class Thing():
    def __init__(self, tileset_to_use: Tileset, tileID):
       self.tileset = tileset_to_use
       self.tileID = tileID
       #assuming we have a thing that holds only one tile, so width and height = 1
       self.width = 1
       self.height = 1
    
    def _addToLayer(self, layer_name,room: Room,x,y):
        posInData = (y*room.content.width)+x
        room._addTileToLayer(layer_name,self.tileset,self.tileID,posInData)
        room.keepFloorLayerOnTop()

    def addToRoom(self, room: Room,x,y):
        room._addTileset(self.tileset)
        # now add the tile to the layer
        self._addToLayer(RoomLayers.THINGS,room,x,y)
       
class ThingWithLink(Thing):
    linkThingCount = 0
    @staticmethod
    def getNextLinkThingNumber():
        ThingWithLink.linkThingCount = ThingWithLink.linkThingCount + 1
        return ThingWithLink.linkThingCount

    def __init__(self, tileset_to_use: Tileset, tileID, link: str ):
        super().__init__(tileset_to_use, tileID )
        self.link = link

    def addToRoom(self,room: Room,x,y):
        room._addTileset(self.tileset)
        # we need to create a layer that fits for our thing
        layerName = "ThingWithLink_layer"+str(ThingWithLink.getNextLinkThingNumber())
        newLayer = Layer(LayerTypes.TILELAYER,0,0,room.content.width,room.content.height,layerName)
        newLayerProperty = LayerProperty("openWebsite", "string", self.link)
        newLayer.properties.append(newLayerProperty)
        room.content.layers.append(newLayer)
        self._addToLayer(layerName,room,x,y)

#Use this class as Entrypoint for the Map
class Entrypoint(Thing):

    def __init__(self, tileset_to_use: Tileset, tileID):
        super().__init__(tileset_to_use, tileID )

    def addToRoom(self,room: Room,x,y):
        room._addTileset(self.tileset)
        # we need to create a layer that fits for our thing
        newLayer = Layer(LayerTypes.TILELAYER,0,0,room.content.width,room.content.height,RoomLayers.START)
        room.content.layers.append(newLayer)
        self._addToLayer(RoomLayers.START,room,x,y)


        

def main():
    print("tiled generator")

    floorTileset = Tileset("floortileset.json")
    bibTileset = Tileset("bibliothek-ext.json")

    # create room
    myroom = Room(10,10)
    myroom.setBackgroundColor(0x55aa55aa) #example how to change room background color
    myroom.setBackgroundTile(floorTileset,23) #example how to add a tile as background layer filled with that tile
    Entrypoint(bibTileset,1).addToRoom(myroom,4,1) #add the entrypoint for the room

    # create a thing and add it to the room 
    door = Thing(bibTileset,11)
    door.addToRoom(myroom,1,1)

    # add the thing a second time
    door.addToRoom(myroom,3,2)

    #with a link
    windowWithLink = ThingWithLink(bibTileset,12,"https://cccs.de")
    windowWithLink.addToRoom(myroom,5,5)
    windowWithLink2 = ThingWithLink(bibTileset,13,"docs\/RC3StyleGuideEssentials.pdf")
    windowWithLink2.addToRoom(myroom,8,8)
 

    # print and export the created room
    print(myroom)
    myroom.toFile('map.json')

if __name__ == "__main__":
    main()


