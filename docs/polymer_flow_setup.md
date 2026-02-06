# Polymer Injection in a Pipe: Basic Blender Setup

This guide outlines a minimal, repeatable setup to get a convincing *first pass* of a polymer “front” moving through a transparent pipe. The emphasis is on clarity and control before fine‑tuning or adding complex shading.

## 1. Pipe (transparent)

1. **Add a Cylinder** (the pipe).
2. **Apply a Solidify modifier** to give it thickness.
3. **Material**:
   - Use **Principled BSDF**.
   - Set **Transmission = 1.0**, **Roughness ≈ 0.05–0.15**, **IOR ≈ 1.45**.
   - Enable **Screen Space Refraction** (Eevee) or use Cycles.

## 2. Polymer “Front” Volume (bulged leading edge)

1. Create a **Curve (Bezier)** that runs along the pipe axis.
2. Add a **Curve Circle** as a profile, then **Curve to Mesh** to make a tube‑like polymer core.
3. For the *leading edge bulge*:
   - Add a **Set Curve Radius** in Geometry Nodes and drive it with a **Map Range** from the curve’s **Spline Parameter** (or use **Trim Curve** + **Set Curve Radius**).
   - Use a **smooth falloff** (e.g., “Ease” interpolation) so the tip inflates gradually.

## 3. Tangled center → straight edges (geometry nodes)

Create a Geometry Nodes modifier on the polymer object and use the radial distance from center to control two behaviors: **tangling (noise)** and **straightness**.

### Key idea
- **Center**: strong noise + higher curve rotations (tangled).
- **Edges**: reduce noise + longer curve segments (straight).

### Node concept (high level)

1. **Position → Separate XYZ**
2. **Vector Length** of XY → “radius”
3. **Map Range** radius to a `tangle_strength` value
   - Example: radius 0 → 1 (tangled), radius 0.35 → 0 (straight)
4. Use `tangle_strength` to:
   - Multiply **Noise** offset for a “knot” deformation
   - Reduce **Spiral rotations** or **trim length** for straighter strands

## 4. Color hint for tangling

Use a **Store Named Attribute** (e.g., `Color`) in Geometry Nodes:

- Feed it a **Color Ramp** driven by the same `tangle_strength`.
- Use a **Material** that reads that attribute in the shader (Attribute node → Base Color).

## 5. Animate the flow

Two quick options:

1. **Trim Curve**: Animate the end value to “grow” the flow along the pipe.
2. **Object translate**: Move the polymer mesh along X with shape keys or driver.

## 6. Basic “starter” parameters

- Pipe inner radius: **0.35**
- Polymer radius: **0.20**
- Bulge max radius: **0.28–0.30**
- Noise scale: **10–15**
- Tangle strength at center: **1.0**
- Tangle strength at edge: **0.0**

---

If you want, we can translate these steps into a minimal, clean **Python script** that builds the Geometry Nodes network so you can iterate quickly on the look.
