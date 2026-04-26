"""
Generates 3 STEP files with known manufacturability issues for testing.
"""
import cadquery as cq
from pathlib import Path

out = Path("tests/sample_files")
out.mkdir(parents=True, exist_ok=True)

# 1. THIN WALL — 0.5mm wall (should flag as critical, min is 2mm)
thin_wall = (
    cq.Workplane("XY")
    .box(20, 20, 10)
    .faces(">X")
    .shell(-0.5)
)
cq.exporters.export(thin_wall, str(out / "thin_wall.step"))
print("✅ Generated: thin_wall.step")

# 2. OVERHANG — 60° overhang (should flag as critical, max is 45°)
overhang = (
    cq.Workplane("XY")
    .box(20, 20, 5)
    .faces(">Z")
    .workplane()
    .transformed(rotate=cq.Vector(60, 0, 0))
    .rect(15, 15)
    .extrude(10)
)
cq.exporters.export(overhang, str(out / "overhang.step"))
print("✅ Generated: overhang.step")

# 3. CLEAN PART — should pass with no issues
clean = (
    cq.Workplane("XY")
    .box(30, 30, 10)
    .edges("|Z")
    .fillet(3)
)
cq.exporters.export(clean, str(out / "clean_part.step"))
print("✅ Generated: clean_part.step")

print("\nAll test STEP files created in tests/sample_files/")
