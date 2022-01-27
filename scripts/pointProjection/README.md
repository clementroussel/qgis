<html><body>
        <h2>Description<\h2>
        <p>Orthogonal projection of a point layer onto a line or multiline vector layer.<\p>
        <h2>Inputs<\h2>
        <p>Axis layer : Should contain a single line or multiline feature onto which points will be projected.<\p>
        <p>Projected layer : Point layer to be projected.<\p>
        <p>Fields to keep : Fields from the projected layer to be kept in the output layer.<\p>
        <p>Digital Terrain Model (DTM) : If provided, point layer features' Z value will be extracted from it. Else, the algorithm will try to extract the Z value of the point layer features' geometry.<\p>
        <p><\p>
        <h2>Output<\h2>
        <p>The output layer is a copy of the projected layer provided whose attribute table contains a new field 'dist' which corresponds to the curvilinear distance of the projected points onto the axis.<\p>
<\body><\html>

# point projection script

---

## Description

