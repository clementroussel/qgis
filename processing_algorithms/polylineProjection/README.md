# polyline projection script

---

## Description

Orthogonal projection of a line or polyline layer onto another line or multiline vector layer.

<p align="center">
   <img src="polylineProjection_figure.png" alt="polyline projection"/>
</p>

## Inputs

- Axis layer : Should contain a single line or multiline feature onto which points will be projected.
- Projected layer : Should contain a single line or multiline feature to be projected.
- Digital Terrain Model (DTM) : If provided, projected layer vertices' Z value will be extracted from it. Else, the algorithm will try to extract the Z value of the projected layer vertices' geometry.
- Interpolate : If checked, the projected layer will be interpolated on the DTM and, consequently, new vertices will be created.

## Output

The output layer is a point layer whose attribute table contains a field 'dist' which corresponds to the curvilinear distance of the projected vertices onto the axis.