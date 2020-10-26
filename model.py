import Rhino.Geometry as rg
import math as m
import simple_comm as c
import simple_ur_script as ur


class Fabrication():

    def __init__(self, fabricate=False, brick_planes=None):
        self.brick_planes = brick_planes
        self.script = ""

    def tcp(self):
        self.script += ur.set_tcp_by_angles(
            0.0, 0.0, 0.0, m.radians(0.0), m.radians(180.0), m.radians(0))

        return self.script

    def pickup_station(self):
        """Example of a method's documentation.

        Parameters
        ----------
        point_x : float
        Description of the first param
        point_y : float
        Description of the second param
        """



        return None

    def place(self):
        """
        this funktion gereates the robotic sequience for placing a brick
        Requires a plane wich describes the possition of the brick"""

        return None

    def sequience(self):
        a = 90

    def visualize(self):
        """ this funktion visualizes the planes wich are sent to the robot"""
        return None

    def send(self):
        """
        this funktion sends the script to the robot."""

        for object in self.wall:
            test =89

        return test


class Brick(object):
    REFERENCE_LENGTH = 25
    REFERENCE_WIDTH = 12
    REFERENCE_HEIGHT = 8

    def __init__(self, plane, length=25, width=12, height=8):
        """Brick containes picking plane, placing plane and geometry

        Parameters
        ----------
        plane : Rhino Geometry plane
        this plane describes the possition and orientation of the Brick

        """
        self.plane = plane
        self.length = length
        self.width = width
        self.height = height

    def dimensions(self):
        """returns the dimenesnions of the brick:

        Returns
        ----------
        [length : float, width : float, height: float]

        """

        return self.length, self.width, self.height

    def pts(self):
        """returns 8 points describing the brick:

        Returns
        ----------
        [pt0 : bottom point at origin,
        pt1 : bottom point at possitive Y,
        pt2 : bottom point at possitive X,
        pt3 : bottom point at possitive X and poossitive Y,
        pt4 : top point at origin,
        pt1 : top point at possitive Y,
        pt2 : top point at possitive X,
        pt3 : top point at possitive X and poossitive Y]

        """

        pt_0 = rg.Point3d(0, 0, 0)
        pt_1 = rg.Point3d(0, self.width, 0)
        pt_2 = rg.Point3d(self.length, 0, 0)
        pt_3 = rg.Point3d(self.length, self.width, 0)

        pt_4 = rg.Point3d(0, 0, self.height)
        pt_5 = rg.Point3d(0, self.width, self.height)
        pt_6 = rg.Point3d(self.length, 0, self.height)
        pt_7 = rg.Point3d(self.length, self.width, self.height)

        b_pts = [pt_0, pt_1, pt_2, pt_3, pt_4, pt_5, pt_6, pt_7]

        return b_pts

    def origin(self):
        """returns the origin plane in the centre of the base of the brick:

        Returns
        ----------
        [Rhino Geometry Plane]

        """
        vec = (self.pts()[3]-self.pts()[0])/2
        origin = self.pts()[0] + vec
        plane = rg.Plane(origin, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
        return plane

    def transformation(self):
        """Transoformation matrix fot transformating the brick to the brick possiotn:

        Returns
        ----------
        [Rhino Geometry Transformation]

        """
        return rg.Transform.PlaneToPlane(self.origin(), self.plane)

    def base_plane(self):
        """Base plane of the transformed brick:

        Returns
        ----------
        [Rhino Geometry Plane]

        """

        p_plane = self.origin()
        p_plane.Transform(self.transformation())
        return p_plane

    def picking_plane(self):
        """Robot's picking plane on the transformed brick:

        Returns
        ----------
        [Rhino Geometry Plane]

        """
        p_plane = self.origin()
        p_pt = p_plane.Origin
        p_plane = rg.Plane(p_pt+rg.Vector3d(0, 0, self.height),
                           p_plane.XAxis, p_plane.YAxis)

        p_plane.Transform(self.transformation())
        return p_plane

    def surface(self):
        """NURB surfaces depicting the brick:

        Returns
        ----------
        [srf0 : base surface,
        srf1 : short edge,
        srf2 : top surface
        srf3 : short edge,
        srf4 : long edge
        srf5 : long edge]

        """
        tran_brick_pts = []
        for pt in self.pts():
            transformation_pt = pt.Clone()
            transformation_pt.Transform(self.transformation())
            tran_brick_pts.append(transformation_pt)

        pt_0, pt_1, pt_2, pt_3, pt_4, pt_5, pt_6, pt_7 = tran_brick_pts

        srf_0 = rg.NurbsSurface.CreateFromPoints(
            [pt_0, pt_1, pt_2, pt_3], 2, 2, 1, 1)
        srf_1 = rg.NurbsSurface.CreateFromPoints(
            [pt_0, pt_1, pt_4, pt_5], 2, 2, 1, 1)
        srf_2 = rg.NurbsSurface.CreateFromPoints(
            [pt_4, pt_5, pt_6, pt_7], 2, 2, 1, 1)
        srf_3 = rg.NurbsSurface.CreateFromPoints(
            [pt_6, pt_7, pt_2, pt_3], 2, 2, 1, 1)
        srf_4 = rg.NurbsSurface.CreateFromPoints(
            [pt_1, pt_3, pt_5, pt_7], 2, 2, 1, 1)
        srf_5 = rg.NurbsSurface.CreateFromPoints(
            [pt_0, pt_2, pt_4, pt_6], 2, 2, 1, 1)

        return (srf_0, srf_1, srf_2, srf_3, srf_4, srf_5)


class Wall():
    def __init__(self, x_cnt, z_cnt):
        """Wall generates and contains the bricks

        Parameters
        ----------
        x_cnt : int
        this number corresponds to the length of the wall (amount of bricks)

        x_cnt : int
        this number corresponds to the hight of the wall
        (amount of brick layers)

        """

        self.x_cnt = x_cnt
        self.z_cnt = z_cnt

        self.b_length = Brick.REFERENCE_LENGTH
        self.b_width = Brick.REFERENCE_WIDTH
        self.b_height = Brick.REFERENCE_HEIGHT

    def brick_possitions(self):
        """Genrates a Rhino Geometry plane for each brick

        Returns
        ----------
        brick_planes : [Rhino Geometry Plane, Rhino Geometry Plane, ...]

        """

        brick_planes = []
        for i in range(self.x_cnt):
            for j in range(self.z_cnt):

                if j % 2 == 0:
                    x_pos = i * (self.b_length + 3)
                    rotation = m.radians(10)
                else:
                    x_pos = i * (self.b_length + 3) + self.b_length/2
                    rotation = m.radians(-10)

                z_pos = j * (self.b_height)

                origin = rg.Point3d(x_pos, 0, z_pos)
                plane = rg.Plane(origin, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
                plane.Rotate(rotation, rg.Vector3d.ZAxis)
                brick_planes.append(plane)

        return brick_planes

    def geometric_model(self):
        """Generates a 3D model of the wall

        Returns
        ----------
        geo : [Rhino Geometry Surface, Rhino Geometry Surface, ...]

        """

        planes = []
        geo = []

        for plane in self.brick_possitions():
            myBrick = Brick(plane)
            planes.append(myBrick.base_plane())

            geo.extend(myBrick.surface())

        return geo

    def fabrication_model(self):
        """Generates all the data necessary for the robotic fabrication
        process and sends the comands to the robot

        Returns script
        ----------
        scritpt : "UR script"
        """

        myFabrication = Fabrication()
        return myFabrication.tcp()
