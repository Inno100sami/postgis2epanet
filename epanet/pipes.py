import json
from shapely.geometry import LineString


class Pipes(object):
    class Pipe(object):
        def __init__(self, id, node1, node2, length, diameter):
            self.id = "Pipe-" + id
            self.node1 = node1
            self.node2 = node2
            self.length = round(length, 3)
            self.diameter = diameter or 0
            self.roughness = 100
            self.minorloss = 0
            self.status = "Open"

        @staticmethod
        def create_header(f):
            f.writelines("[PIPES]\n")
            f.writelines(";{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n"
                         .format("ID\t".expandtabs(20),
                                 "Node1\t".expandtabs(15),
                                 "Node2\t".expandtabs(15),
                                 "Length\t".expandtabs(10),
                                 "Diameter\t".expandtabs(10),
                                 "Roughness\t".expandtabs(10),
                                 "MinorLoss\t".expandtabs(10),
                                 "Status\t".expandtabs(15)
                                 ))

        def add(self, f):
            f.writelines("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n"
                         .format("{0}\t".format(self.id).expandtabs(20),
                                 "{0}\t".format(str(self.node1)).expandtabs(15),
                                 "{0}\t".format(str(self.node2)).expandtabs(15),
                                 "{0}\t".format(str(self.length)).expandtabs(10),
                                 "{0}\t".format(str(self.diameter)).expandtabs(10),
                                 "{0}\t".format(str(self.roughness)).expandtabs(10),
                                 "{0}\t".format(str(self.minorloss)).expandtabs(10),
                                 "{0}\t".format(self.status).expandtabs(15)
                                 ))

    def __init__(self, wss_id, coords):
        self.wss_id = wss_id
        self.coords = coords
        self.pipes = []

    def get_data(self, db):
        query = " SELECT pipe_id, pipe_size, ST_AsGeoJSON(st_multi(geom)) as geojson " \
                "FROM pipeline WHERE wss_id={0} ".format(str(self.wss_id))
        result = db.execute(query)
        for data in result:
            pipe_id = data[0]
            pipe_size = data[1]
            geojson = json.loads(data[2])
            coordinates = geojson['coordinates'][0]
            for i in range(0, len(coordinates) - 1):

                x1 = round(coordinates[i][0], 6)
                y1 = round(coordinates[i][1], 6)
                key1 = ",".join([str(x1), str(y1)])
                if key1 in self.coords.coordMap and self.coords.coordMap[key1]:
                    coord1 = self.coords.coordMap[key1]
                    j = i + 1
                    x2 = round(coordinates[j][0], 6)
                    y2 = round(coordinates[j][1], 6)
                    key2 = ",".join([str(x2), str(y2)])

                    if key1 != key2 and key2 in self.coords.coordMap and self.coords.coordMap[key2]:
                        coord2 = self.coords.coordMap[key2]
                        node1 = coord1.id
                        node2 = coord2.id

                        xy_list = [[coord1.lon_utm, coord1.lat_utm], [coord2.lon_utm, coord2.lat_utm]]
                        line = LineString(xy_list)

                        length = line.length
                        _id = "{0}-{1}".format(pipe_id, i)
                        pipe = Pipes.Pipe(_id, node1, node2, length, pipe_size)
                        self.pipes.append(pipe)

    def export(self, f):
        Pipes.Pipe.create_header(f)
        for pipe in self.pipes:
            pipe.add(f)
        f.writelines("\n")