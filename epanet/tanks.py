from epanet.coordinates import Coordinates
import shapefile
from epanet.layer_base import LayerBase


class Tanks(LayerBase):
    class Tank(object):
        def __init__(self, data):
            self.id = data["id"]
            self.elevation = data["elevation"] or 0
            self.capacity = data["capacity"] or 0
            self.max_level = 1.5
            self.lon = round(data["lon"], 6)
            self.lat = round(data["lat"], 6)
            self.diameter = 5
            self.min_vol = self.capacity
            self.vol_curve = ""

        @staticmethod
        def create_header(f):
            f.writelines("[TANKS]\n")
            f.writelines(";{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n"
                         .format("ID\t".expandtabs(20),
                                 "Elevation\t".expandtabs(12),
                                 "InitLevel\t".expandtabs(12),
                                 "MinLevel\t".expandtabs(12),
                                 "MaxLevel\t".expandtabs(12),
                                 "Diameter\t".expandtabs(12),
                                 "MinVol\t".expandtabs(12),
                                 "VolCurve"
                                 ))

        def add(self, f):
            f.writelines(" {0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t;\n"
                         .format("{0}\t".format(self.id).expandtabs(20),
                                 "{0}\t".format(str(self.elevation)).expandtabs(12),
                                 "{0}\t".format(str(self.max_level * 0.5)).expandtabs(12),
                                 "{0}\t".format(str(self.max_level * 0.1)).expandtabs(12),
                                 "{0}\t".format(str(self.max_level)).expandtabs(12),
                                 "{0}\t".format(str(self.diameter)).expandtabs(12),
                                 "{0}\t".format(str(self.min_vol)).expandtabs(12),
                                 "{0}\t".format(str(self.vol_curve)).expandtabs(16)
                                 ))

    def __init__(self, wss_id, coords, config):
        super().__init__("tanks", wss_id, config)
        self.coords = coords
        self.tanks = []

    def get_data(self, db):
        query = self.get_sql().format(str(self.wss_id))
        result = db.execute(query)
        for data in result:
            t = Tanks.Tank(data)
            self.tanks.append(t)
            coord = Coordinates.Coordinate(data)
            self.coords.add_coordinate(coord)

    def export(self, f):
        Tanks.Tank.create_header(f)
        for t in self.tanks:
            t.add(f)
        f.writelines("\n")

    def export_shapefile(self, f):
        if len(self.tanks) == 0:
            return
        filename = self.get_file_path(f)
        with shapefile.Writer(filename) as _shp:
            _shp.autoBalance = 1
            _shp.field('dc_id', 'C', 254)
            _shp.field('elevation', 'N', 20)
            _shp.field('initiallev', 'N', 20)
            _shp.field('minimumlev', 'N', 20)
            _shp.field('maximumlev', 'N', 20)
            _shp.field('diameter', 'N', 20)
            _shp.field('minimumvol', 'N', 20)
            _shp.field('volumecurv', 'N', 20)
            for t in self.tanks:
                _shp.point(float(t.lon), float(t.lat))
                _shp.record(t.id, t.elevation, t.capacity * 0.5, t.capacity * 0.1, t.capacity,
                            t.diameter, t.min_vol, t.vol_curve)
            _shp.close()
        self.createProjection(filename)
