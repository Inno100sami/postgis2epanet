from epanet.coordinates import Coordinates


class Reservoirs(object):
    class Reservoir(object):
        def __init__(self, id, elevation, srctype, lon, lat):
            self.id = "{0}-{1}".format(srctype, str(id))
            self.elevation = elevation or 0
            self.pattern = ""
            self.lon = round(lon, 6)
            self.lat = round(lat, 6)

        @staticmethod
        def create_header(f):
            f.writelines("[RESERVOIRS]\n")
            f.writelines(";{0}{1}{2}\n"
                         .format("ID\t".expandtabs(20),
                                 "Head\t".expandtabs(10),
                                 "Pattern\t".expandtabs(10)
                                 ))

        def add(self, f):
            f.writelines("{0}{1}{2}\n"
                         .format("{0}\t".format(self.id).expandtabs(20),
                                 "{0}\t".format(str(self.elevation)).expandtabs(10),
                                 "{0}\t".format(str(self.pattern)).expandtabs(10)
                                 ))

    def __init__(self, wss_id, coords):
        self.wss_id = wss_id
        self.coords = coords
        self.reservoirs = []
        self.epsg_utm = 32736

    def get_data(self, db):
        query = " SELECT watersource_id as id, st_x(geom) as lon, st_y(geom) as lat, elevation, source_type,    "
        query += " st_x(st_transform(geom,{0})) as lon_utm, st_y(st_transform(geom,{0})) as lat_utm  "\
            .format(self.epsg_utm)
        query += "FROM watersource WHERE wss_id={0} ".format(str(self.wss_id))
        result = db.execute(query)
        for data in result:
            id = data[0]
            lon = data[1]
            lat = data[2]
            elevation = data[3]
            srctype = data[4]
            lon_utm = data[5]
            lat_utm = data[6]
            r = Reservoirs.Reservoir(id, elevation, srctype, lon, lat)
            self.reservoirs.append(r)

            coord = Coordinates.Coordinate(r.id, r.lon, r.lat, r.elevation, lon_utm, lat_utm)
            self.coords.add_coordinate(coord)

    def export(self, f):
        Reservoirs.Reservoir.create_header(f)
        for r in self.reservoirs:
            r.add(f)
        f.writelines("\n")