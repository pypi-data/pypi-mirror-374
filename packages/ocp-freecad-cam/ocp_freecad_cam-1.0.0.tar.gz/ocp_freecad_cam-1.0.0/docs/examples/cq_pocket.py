import cadquery as cq

from ocp_freecad_cam import Endmill, Job

wp = (
    cq.Workplane()
    .rect(10, 10)
    .extrude(5)
    .faces(">Z")
    .workplane()
    .rect(8, 8)
    .cutBlind(-2)
    .faces(">Z")
    .rect(10, 2)
    .cutBlind(-2)
)

pocket = wp.faces(">Z[1]")
top = wp.faces(">Z").workplane()
tool = Endmill(diameter=1)
job = Job(top, wp).pocket(pocket, tool=tool, pattern="offset")
