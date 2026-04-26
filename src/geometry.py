import cadquery as cq
import numpy as np
from typing import List, Dict, Tuple


def face_centroid(face) -> Tuple[float, float, float]:
    c = face.Center()
    return (round(c.x, 3), round(c.y, 3), round(c.z, 3))


def face_normal(face) -> Tuple[float, float, float]:
    n = face.normalAt()
    return (round(n.x, 3), round(n.y, 3), round(n.z, 3))


def nearby(loc1, loc2, threshold=5.0) -> bool:
    return sum((a - b) ** 2 for a, b in zip(loc1, loc2)) ** 0.5 < threshold


def analyze_overhangs(shape, max_angle=45.0) -> List[Dict]:
    issues = []
    all_faces = list(shape.faces())
    min_z = min(face.Center().z for face in all_faces)

    for face in all_faces:
        try:
            normal = face_normal(face)
            nz = normal[2]
            if nz >= 0:
                continue
            centroid = face_centroid(face)
            if abs(centroid[2] - min_z) < 0.5:
                continue
            angle = round(np.degrees(np.arcsin(abs(nz))), 2)
            if angle > max_angle:
                if not any(nearby(centroid, i['location']) for i in issues):
                    issues.append({
                        "issue_type": "overhang",
                        "location": centroid,
                        "angle_degrees": angle,
                        "severity": "critical" if angle > 70 else "warning",
                        "fix": f"Overhang at {angle}° exceeds printable limit of {max_angle}° → requires support structures → increases material cost and print time. Redesign to reduce angle or add chamfer."
                    })
        except Exception:
            continue
    return issues


def analyze_thin_walls(shape, min_thickness=2.0) -> List[Dict]:
    issues = []
    solid = shape.val()

    for face in shape.faces():
        try:
            centroid = face.Center()
            normal = face.normalAt()
            origin = centroid.add(normal.multiply(-0.01))
            direction = normal.multiply(-1)

            from OCP.gp import gp_Pnt, gp_Dir, gp_Lin
            from OCP.BRepIntCurveSurface_Gen import BRepIntCurveSurface_Gen

            ray_origin = gp_Pnt(origin.x, origin.y, origin.z)
            ray_dir = gp_Dir(direction.x, direction.y, direction.z)
            line = gp_Lin(ray_origin, ray_dir)

            inter = BRepIntCurveSurface_Gen()
            inter.Init(solid, line, 1e-6)

            distances = []
            while inter.More():
                pt = inter.Pnt()
                dist = origin.distance(cq.Vector(pt.X(), pt.Y(), pt.Z()))
                distances.append(dist)
                inter.Next()

            if len(distances) >= 2:
                distances.sort()
                thickness = distances[1] - distances[0]
                if 0 < thickness < min_thickness:
                    loc = (round(centroid.x, 3), round(centroid.y, 3), round(centroid.z, 3))
                    if not any(nearby(loc, i['location']) for i in issues):
                        issues.append({
                            "issue_type": "thin_wall",
                            "location": loc,
                            "thickness_mm": round(thickness, 3),
                            "severity": "critical" if thickness < 1.0 else "warning",
                            "fix": f"Wall at {round(thickness,2)}mm is below minimum {min_thickness}mm → risk of structural failure during CNC or print. Increase wall thickness in CAD."
                        })
        except Exception:
            continue
    return issues


def analyze_sharp_edges(shape, min_radius=1.0) -> List[Dict]:
    issues = []
    for edge in shape.edges():
        try:
            verts = edge.Vertices()
            if len(verts) < 2:
                continue
            v1 = cq.Vector(verts[0].X, verts[0].Y, verts[0].Z)
            v2 = cq.Vector(verts[1].X, verts[1].Y, verts[1].Z)
            length = v1.sub(v2).Length
            if 0 < length < min_radius:
                loc = (round((v1.x+v2.x)/2,3), round((v1.y+v2.y)/2,3), round((v1.z+v2.z)/2,3))
                if not any(nearby(loc, i['location']) for i in issues):
                    issues.append({
                        "issue_type": "sharp_edge",
                        "location": loc,
                        "length_mm": round(length, 3),
                        "severity": "warning",
                        "fix": f"Edge radius {round(length,2)}mm below minimum {min_radius}mm → CNC tool cannot navigate sharp internal corner. Add fillet of at least {min_radius}mm."
                    })
        except Exception:
            continue
    return issues
