# cross-profiles script

---

## Description

Generate regularly spaced cross-profiles along an axis.

## Inputs

- Axis layer : Should contain a single line or multiline feature onto which points will be projected.
- Distance between two profiles : self-explained.
- Profiles length : self-explained.
- Extent layer : If provided, cross-profiles will be ajusted according to this layer.
- Profiles subdivision length : Cross-profiles geometries are densified by adding additional vertices. This value indicates the maximum distance between two consecutive vertices.
- Digital Terrain Model (DTM) : Cross-profiles vertices Z value will be extracted from it.

## Output

A cross-profiles layer whose attribute table contains a field 'dist' and a field 'z min' that can be used to approximate a longitudinal profile.