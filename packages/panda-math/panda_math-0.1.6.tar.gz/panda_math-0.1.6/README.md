# Panda Math

A high-performance Python library for vector and matrix operations, designed specifically for mathematical computing and game development. Built with NumPy compatibility and modern Python features.

## Features

- **Complete Vector Support**: 2D, 3D, and 4D vector classes with full mathematical operations
- **Comprehensive Matrix Operations**: Full-featured Matrix class with linear algebra support
- **Rich Operator Overloading**: Natural mathematical syntax with `+`, `-`, `*`, `/`, `//`, `%`, `**`
- **NumPy Integration**: Seamless conversion to/from NumPy arrays
- **Type Safety**: Full type hints and generic base classes
- **Performance Optimized**: Efficient implementations for real-time applications
- **Game Development Ready**: Cross products, normalization, distance calculations, transformations
- **Advanced Linear Algebra**: Determinants, inverses, eigenvalues, LU decomposition
- **3D Graphics Support**: Transformation matrices, projection matrices, view matrices

## Installation

```bash
pip install panda-math
```

## Quick Start

```python
from panda_math import Vector2, Vector3, Vector4, Matrix, vec2, vec3, vec4

# Create vectors
v1 = Vector2(3, 4)
v2 = vec3(1, 2, 3)  # Convenient aliases
v3 = Vector4([1, 0, 0, 1])  # From iterable

# Create matrices
m1 = Matrix([[1, 2], [3, 4]])
m2 = Matrix.identity(3)
m3 = Matrix([v2, Vector3(4, 5, 6)])  # From vectors

# Basic operations
result = v1 + Vector2(1, 1)  # Vector2(4, 5)
scaled = v2 * 2.5           # Vector3(2.5, 5.0, 7.5)
magnitude = v2.magnitude    # 3.74...

# Matrix operations
transformed = m1 * v1       # Matrix-vector multiplication
inverted = m1.inverse()     # Matrix inverse
det = m1.determinant()      # Determinant calculation

# Advanced operations
normalized = v2.normalize()
distance = v1.distance_to(Vector2(0, 0))
dot_product = v2.dot(Vector3(1, 1, 1))
```

## Vector Classes

### Vector2

Perfect for 2D graphics, UI positioning, and planar mathematics.

```python
from panda_math import Vector2

# Creation
pos = Vector2(10, 20)
velocity = Vector2([5, -3])  # From list/tuple

# Properties
print(pos.x, pos.y)          # 10 20
print(pos.magnitude)         # 22.36...
print(len(pos))             # 2

# Operations
new_pos = pos + velocity * 0.016  # Frame-based movement
normalized_vel = velocity.normalize()
```

### Vector3

Essential for 3D graphics, physics simulations, and spatial calculations.

```python
from panda_math import Vector3

# 3D operations
forward = Vector3(0, 0, 1)
up = Vector3(0, 1, 0)
right = forward.cross(up)    # Cross product: Vector3(1, 0, 0)

# Lighting calculations
light_dir = Vector3(1, 1, 1).normalize()
surface_normal = Vector3(0, 1, 0)
intensity = light_dir.dot(surface_normal)
```

### Vector4

Ideal for homogeneous coordinates, quaternions, and RGBA colors.

```python
from panda_math import Vector4

# Homogeneous coordinates
point = Vector4(10, 20, 30, 1)
direction = Vector4(0, 1, 0, 0)

# Color manipulation
red = Vector4(1.0, 0.0, 0.0, 1.0)  # RGBA
transparent_red = red * Vector4(1, 1, 1, 0.5)
```

## Matrix Class

The Matrix class provides comprehensive linear algebra operations with seamless vector integration.

### Creating Matrices

```python
from panda_math import Matrix, Vector2, Vector3

# From nested lists
m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# From dimensions (creates zero matrix)
m2 = Matrix(rows=3, cols=3)

# From vectors (as rows)
v1 = Vector3(1, 2, 3)
v2 = Vector3(4, 5, 6)
m3 = Matrix([v1, v2])

# Identity matrices
identity = Matrix.identity(4)

# From numpy arrays
import numpy as np
np_array = np.array([[1, 2], [3, 4]])
m4 = Matrix.from_numpy(np_array)
```

### Matrix Operations

```python
# Basic arithmetic
m1 = Matrix([[1, 2], [3, 4]])
m2 = Matrix([[5, 6], [7, 8]])

addition = m1 + m2        # Matrix addition
subtraction = m1 - m2     # Matrix subtraction
multiplication = m1 * m2  # Matrix multiplication
scalar_mult = m1 * 2.5    # Scalar multiplication

# Matrix-vector multiplication
v = Vector2(1, 2)
result = m1 * v          # Returns Vector2

# Advanced operations
transposed = m1.transpose()
determinant = m1.determinant()
inverse = m1.inverse()
trace = m1.trace()
```

### Linear Algebra Features

```python
m = Matrix([[4, 2], [1, 3]])

# Properties
is_singular = m.is_singular()
is_symmetric = m.is_symmetric()
is_orthogonal = m.is_orthogonal()
matrix_rank = m.rank()

# Decompositions
L, U = m.lu_decomposition()          # LU decomposition
eigenvals, eigenvecs = m.eigenvectors()  # Eigendecomposition

# Matrix forms
rref = m.reduced_row_echelon_form()
ref = m.row_echelon_form()

# Access rows and columns
first_row = m.row(0)     # Returns appropriate Vector type
first_col = m.col(0)     # Returns appropriate Vector type
```

## 3D Graphics and Transformations

Panda Math includes comprehensive support for 3D graphics transformations:

### 2D Transformations

```python
from panda_math import (
    rotation_matrix_2d, scaling_matrix_2d, shear_matrix_2d,
    reflection_matrix_2d, transform_point_2d
)

# Create transformation matrices
rotation = rotation_matrix_2d(np.pi / 4)  # 45 degree rotation
scaling = scaling_matrix_2d(2.0, 1.5)     # Scale x by 2, y by 1.5
shear = shear_matrix_2d(0.5, 0)           # Shear in x direction

# Transform points
point = Vector2(1, 1)
rotated = rotation * point
scaled = scaling * point

# Combined transformations
transform = scaling * rotation  # Apply rotation, then scaling
result = transform * point
```

### 3D Transformations

```python
from panda_math import (
    rotation_matrix_3d, rotation_matrix_3d_arbitrary,
    scaling_matrix_3d, transform_point_3d
)

# Axis-aligned rotations
rot_x = rotation_matrix_3d('x', np.pi / 2)  # 90° around X-axis
rot_y = rotation_matrix_3d('y', np.pi / 4)  # 45° around Y-axis
rot_z = rotation_matrix_3d('z', np.pi / 6)  # 30° around Z-axis

# Arbitrary axis rotation
axis = Vector3(1, 1, 0).normalize()
arbitrary_rot = rotation_matrix_3d_arbitrary(axis, np.pi / 3)

# 3D transformations
point_3d = Vector3(1, 2, 3)
rotated_3d = rot_x * point_3d
```

### Homogeneous Coordinates (4D)

```python
from panda_math import (
    translation_matrix_4d, scaling_matrix_4d, rotation_matrix_4d_x,
    transform_point_homogeneous
)

# 4x4 transformation matrices for 3D graphics
translation = translation_matrix_4d(5, 10, -2)
scaling = scaling_matrix_4d(2, 2, 2)
rotation = rotation_matrix_4d_x(np.pi / 2)

# Combine transformations (order matters!)
transform = translation * scaling * rotation

# Transform 3D points using homogeneous coordinates
point = Vector3(1, 2, 3)
transformed = transform_point_homogeneous(point, transform)
```

### Camera and Projection Matrices

```python
from panda_math import (
    look_at_matrix, perspective_projection_matrix,
    orthographic_projection_matrix
)

# Create a camera view matrix
eye = Vector3(0, 0, 10)      # Camera position
target = Vector3(0, 0, 0)    # Look at origin
up = Vector3(0, 1, 0)        # Up direction
view_matrix = look_at_matrix(eye, target, up)

# Perspective projection
fov = np.pi / 3              # 60 degrees field of view
aspect = 16.0 / 9.0          # Aspect ratio
near = 0.1                   # Near clipping plane
far = 100.0                  # Far clipping plane
perspective = perspective_projection_matrix(fov, aspect, near, far)

# Orthographic projection
ortho = orthographic_projection_matrix(-10, 10, -10, 10, 0.1, 100)

# Complete 3D graphics pipeline
mvp_matrix = perspective * view_matrix * transform
```

## Supported Operations

### Arithmetic Operations

```python
v1 = Vector3(1, 2, 3)
v2 = Vector3(4, 5, 6)
m1 = Matrix([[1, 2], [3, 4]])
m2 = Matrix([[5, 6], [7, 8]])

# Vector-vector operations
addition = v1 + v2        # Element-wise addition
subtraction = v1 - v2     # Element-wise subtraction
multiplication = v1 * v2  # Element-wise multiplication
division = v1 / v2        # Element-wise division

# Matrix-matrix operations
m_add = m1 + m2          # Matrix addition
m_mult = m1 * m2         # Matrix multiplication
m_scalar = m1 * 2.5      # Scalar multiplication

# Matrix-vector operations
transformed = m1 * Vector2(1, 2)  # Returns Vector2

# Scalar operations
scaled = v1 * 2.5         # Scalar multiplication
divided = v1 / 2          # Scalar division
powered = v1 ** 2         # Element-wise power
```

### In-Place Operations

```python
v = Vector3(1, 2, 3)
v += Vector3(1, 1, 1)     # v is now Vector3(2, 3, 4)
v *= 2                    # v is now Vector3(4, 6, 8)
v.reverse()               # Negates all components in-place

m = Matrix([[1, 2], [3, 4]])
m += Matrix([[1, 1], [1, 1]])  # Element-wise addition
m *= 2                         # Scalar multiplication
```

### Comparison Operations

```python
v1 = Vector2(1, 2)
v2 = Vector2(3, 4)
m1 = Matrix([[1, 2], [3, 4]])
m2 = Matrix([[1, 2], [3, 4]])

print(v1 < v2)            # True (all components less)
print(v1 == Vector2(1, 2)) # True
print(v1 >= 0)            # True (all components >= 0)
print(m1 == m2)           # True (matrices are equal)
```

## Advanced Features

### NumPy Integration

```python
import numpy as np
from panda_math import Vector3, Matrix

# Convert vectors to NumPy
v = Vector3(1, 2, 3)
array = v.to_numpy()      # np.array([1, 2, 3])

# Convert matrices to NumPy
m = Matrix([[1, 2], [3, 4]])
np_matrix = m.to_numpy()  # np.array([[1, 2], [3, 4]])

# Create from NumPy
np_array = np.array([4, 5, 6, 7])
v2 = Vector3.from_numpy(np_array)  # Uses first 3 elements

np_matrix = np.array([[5, 6], [7, 8]])
m2 = Matrix.from_numpy(np_matrix)
```

### Conversion Between Dimensions

```python
from panda_math import vec2_to_vec3, vec3_to_vec2, vec3_to_vec4

# Convert between vector dimensions
v2d = Vector2(10, 20)
v3d = vec2_to_vec3(v2d, z=0)      # Add z component
v4d = vec3_to_vec4(v3d, w=1)      # Add w component

# Project back down
projected = vec3_to_vec2(v3d)     # Drop z component
```

### Matrix Construction Utilities

```python
# Create matrices from rows or columns
row1 = Vector3(1, 2, 3)
row2 = Vector3(4, 5, 6)
row3 = Vector3(7, 8, 9)
matrix_from_rows = Matrix.from_rows(row1, row2, row3)

col1 = Vector3(1, 4, 7)
col2 = Vector3(2, 5, 8)
col3 = Vector3(3, 6, 9)
matrix_from_cols = Matrix.from_cols(col1, col2, col3)

# Apply functions to matrix elements
doubled = matrix.apply(lambda x: x * 2)
```

## Common Use Cases

### Game Development

```python
# Player movement with transformation matrices
player_pos = Vector3(0, 0, 0)
player_rotation = rotation_matrix_3d('y', np.pi / 4)  # 45° turn
movement_input = Vector3(0, 0, 1)  # Forward

# Transform movement by player rotation
world_movement = player_rotation * movement_input
new_position = player_pos + world_movement * speed * delta_time

# Camera system
camera_transform = look_at_matrix(
    Vector3(player_pos.x, player_pos.y + 5, player_pos.z - 10),
    player_pos,
    Vector3(0, 1, 0)
)
```

### Physics Simulations

```python
# Rigid body transformations
position = Vector3(0, 0, 0)
rotation = rotation_matrix_3d_arbitrary(Vector3(1, 1, 0), np.pi / 6)
scale = scaling_matrix_3d(2, 1, 1)

# Compose transformation matrix
model_matrix = translation_matrix_4d(*position) * rotation * scale

# Transform object vertices
vertices = [Vector3(1, 1, 1), Vector3(-1, 1, 1), Vector3(-1, -1, 1)]
transformed_vertices = [transform_point_homogeneous(v, model_matrix) for v in vertices]
```

### Computer Graphics Pipeline

```python
# Complete 3D rendering pipeline
model_matrix = translation_matrix_4d(0, 0, -5)
view_matrix = look_at_matrix(
    Vector3(0, 0, 10),    # Camera position
    Vector3(0, 0, 0),     # Look at target
    Vector3(0, 1, 0)      # Up vector
)
projection_matrix = perspective_projection_matrix(
    np.pi / 3,    # 60° FOV
    16/9,         # Aspect ratio
    0.1,          # Near plane
    100.0         # Far plane
)

# MVP (Model-View-Projection) matrix
mvp = projection_matrix * view_matrix * model_matrix

# Transform vertices
vertex = Vector3(1, 1, 1)
screen_space = transform_point_homogeneous(vertex, mvp)
```

### Linear Algebra Applications

```python
# Solve linear systems using matrix operations
# Ax = b  =>  x = A^(-1) * b
A = Matrix([[2, 1], [1, 1]])
b = Vector2(3, 2)
solution = A.inverse() * b

# Principal Component Analysis setup
data_matrix = Matrix([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

# Compute covariance matrix
centered = data_matrix - data_matrix.trace() / 3  # Simplified centering
covariance = centered.transpose() * centered

# Find principal components
eigenvalues, eigenvectors = covariance.eigenvectors()
```

## Performance Tips

1. **Use in-place operations** (`+=`, `*=`, etc.) when possible to avoid creating new objects
2. **Normalize vectors once** and reuse when the direction is needed multiple times
3. **Use appropriate vector dimensions** - don't use Vector4 when Vector2 suffices
4. **Leverage NumPy conversion** for bulk operations on many vectors
5. **Pre-compute transformation matrices** for repeated use
6. **Use homogeneous coordinates** for complex 3D transformations
7. **Cache matrix inverses** if used multiple times

## API Reference

### VectorBase (Generic Base Class)

- `magnitude: float` - Vector length/magnitude
- `normalize() -> T` - Returns normalized vector (unit length)
- `distance_to(other: T) -> float` - Euclidean distance to another vector
- `dot(other: T) -> float` - Dot product with another vector
- `reverse()` - Negates all components in-place
- `reversed: T` - Returns a new vector with negated components
- `to_list() -> List[float]` - Convert to Python list
- `to_tuple() -> Tuple[float, ...]` - Convert to Python tuple
- `to_numpy() -> np.ndarray` - Convert to NumPy array
- `from_numpy(array: np.ndarray) -> T` - Create from NumPy array
- `from_iterable(iterable: Iterable) -> T` - Create from any iterable

### Vector3 Specific

- `cross(other: Vector3) -> Vector3` - Cross product (3D only)

### Matrix Class Methods

- `transpose() -> Matrix` - Matrix transpose
- `determinant() -> float` - Calculate determinant
- `inverse() -> Matrix` - Matrix inverse
- `trace() -> float` - Sum of diagonal elements
- `rank() -> int` - Matrix rank
- `is_singular() -> bool` - Check if matrix is singular
- `is_symmetric() -> bool` - Check if matrix is symmetric
- `is_orthogonal() -> bool` - Check if matrix is orthogonal
- `lu_decomposition() -> Tuple[Matrix, Matrix]` - LU decomposition
- `eigenvectors() -> Tuple[List[float], List[Matrix]]` - Eigenvalues and eigenvectors
- `row(i: int)` - Get row as vector
- `col(j: int)` - Get column as vector
- `minor(row: int, col: int) -> Matrix` - Calculate minor matrix
- `cofactor(row: int, col: int) -> float` - Calculate cofactor
- `adjugate() -> Matrix` - Calculate adjugate matrix
- `row_echelon_form() -> Matrix` - Convert to row echelon form
- `reduced_row_echelon_form() -> Matrix` - Convert to RREF
- `apply(func: Callable) -> Matrix` - Apply function to all elements

### Matrix Class Methods

- `Matrix.identity(size: int) -> Matrix` - Create identity matrix
- `Matrix.from_rows(*rows) -> Matrix` - Create from row vectors
- `Matrix.from_cols(*cols) -> Matrix` - Create from column vectors
- `Matrix.from_numpy(array: np.ndarray) -> Matrix` - Create from NumPy array

### Transformation Functions

#### 2D Transformations

- `rotation_matrix_2d(angle: float) -> Matrix`
- `scaling_matrix_2d(sx: float, sy: float = None) -> Matrix`
- `shear_matrix_2d(shx: float = 0, shy: float = 0) -> Matrix`
- `reflection_matrix_2d(axis: str = 'x') -> Matrix`
- `transform_point_2d(point: Vector2, matrix: Matrix, translation: Vector2 = None) -> Vector2`

#### 3D Transformations

- `rotation_matrix_3d(axis: str, angle: float) -> Matrix`
- `rotation_matrix_3d_arbitrary(axis: Vector3, angle: float) -> Matrix`
- `scaling_matrix_3d(sx: float, sy: float = None, sz: float = None) -> Matrix`
- `shear_matrix_3d(**kwargs) -> Matrix`
- `reflection_matrix_3d(plane: str = 'xy') -> Matrix`
- `transform_point_3d(point: Vector3, matrix: Matrix, translation: Vector3 = None) -> Vector3`

#### 4D Homogeneous Transformations

- `translation_matrix_4d(tx: float, ty: float, tz: float) -> Matrix`
- `scaling_matrix_4d(sx: float, sy: float = None, sz: float = None) -> Matrix`
- `rotation_matrix_4d_x/y/z(angle: float) -> Matrix`
- `transform_point_homogeneous(point: Vector3, transform: Matrix) -> Vector3`

#### Graphics and Projection

- `perspective_projection_matrix(fov: float, aspect: float, near: float, far: float) -> Matrix`
- `orthographic_projection_matrix(left: float, right: float, bottom: float, top: float, near: float, far: float) -> Matrix`
- `look_at_matrix(eye: Vector3, target: Vector3, up: Vector3) -> Matrix`

#### Utilities

- `interpolate_matrices(a: Matrix, b: Matrix, t: float) -> Matrix`

## Requirements

- Python 3.7+
- NumPy

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.