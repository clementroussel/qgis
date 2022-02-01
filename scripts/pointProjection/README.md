# point projection script

---

## Description

Orthogonal projection of a point layer onto a line or multiline vector layer.

![point projection]("pointProjection_figure.png")

## Inputs

- Axis layer : Should contain a single line or multiline feature onto which points will be projected.
- Projected layer : Point layer to be projected.
- Fields to keep : Fields from the projected layer to be kept in the output layer.
- Digital Terrain Model (DTM) : If provided, point layer features' Z value will be extracted from it. Else, the algorithm will try to extract the Z value of the point layer features' geometry.

## Output

The output layer is a copy of the projected layer provided whose attribute table contains a new field 'dist' which corresponds to the curvilinear distance of the projected points onto the axis.