"""2D and 3D truss analysis using the direct stiffness method.

Supports pin-jointed truss structures commonly used in:
- Aircraft internal structures (wing ribs, fuselage frames)
- Spacecraft truss assemblies (deployable structures, berthing mechanisms)
- Launch vehicle interstage adapters
- Drone and UAV airframes

References:
    - Megson, "Aircraft Structures for Engineering Students", 6th Ed.
      Direct stiffness method for pin-jointed trusses (Chapter 16).
    - Przemieniecki, "Theory of Matrix Structural Analysis"
      Formulation of element stiffness matrices and global assembly.
"""

import numpy as np

G_STD = 9.80665


def truss_analysis(
    nodes: list[list[float]],
    elements: list[list[int]],
    element_properties: list[dict],
    constraints: list[dict],
    loads: list[dict],
) -> dict:
    """Analyze a pin-jointed truss using the direct stiffness method.

    Args:
        nodes: List of [x, y] or [x, y, z] coordinates for each node.
            Node indices are 0-based.
        elements: List of [node_i, node_j] pairs defining each truss member.
        element_properties: List of dicts, one per element, with:
            - youngs_modulus_pa: E (Pa)
            - area_m2: Cross-sectional area (m²)
        constraints: List of dicts with:
            - node: Node index
            - fixed_dof: List of fixed DOFs, e.g. [0, 1] for x,y fixed in 2D
        loads: List of dicts with:
            - node: Node index
            - force: [Fx, Fy] or [Fx, Fy, Fz] in Newtons

    Returns:
        dict with member forces, reactions, node displacements, and utilization.
    """
    n_nodes = len(nodes)
    n_elements = len(elements)

    if n_elements == 0:
        raise ValueError("At least one element required")
    if len(element_properties) != n_elements:
        raise ValueError("element_properties must have same length as elements")
    if n_nodes < 2:
        raise ValueError("At least 2 nodes required")

    # Detect dimensionality from first node
    dim = len(nodes[0])
    if dim not in (2, 3):
        raise ValueError("Nodes must be 2D [x, y] or 3D [x, y, z]")

    # Validate all nodes have same dimension
    for i, node in enumerate(nodes):
        if len(node) != dim:
            raise ValueError(f"Node {i} has {len(node)} coordinates, expected {dim}")

    n_dof = n_nodes * dim

    # Global stiffness matrix
    K = np.zeros((n_dof, n_dof))  # noqa: N806
    # Force vector
    F = np.zeros(n_dof)  # noqa: N806
    # Displacement vector

    # Assemble global stiffness matrix
    element_results = []

    for e_idx, (elem, props) in enumerate(zip(elements, element_properties)):
        i_node, j_node = elem
        if i_node < 0 or i_node >= n_nodes or j_node < 0 or j_node >= n_nodes:
            raise ValueError(f"Element {e_idx}: invalid node index")

        # noqa: N806
        E = props.get("youngs_modulus_pa", 0.0)  # noqa: N806
        # noqa: N806
        A = props.get("area_m2", 0.0)  # noqa: N806
        if E <= 0 or A <= 0:
            raise ValueError(f"Element {e_idx}: E and A must be > 0")

        xi, yi = nodes[i_node][:2]
        xj, yj = nodes[j_node][:2]

        if dim == 3:
            zi, zj = nodes[i_node][2], nodes[j_node][2]
            dx, dy, dz = xj - xi, yj - yi, zj - zi
            # noqa: N806
            L = np.sqrt(dx**2 + dy**2 + dz**2)  # noqa: N806
            if L < 1e-12:
                raise ValueError(
                    f"Element {e_idx}: nodes {i_node} and {j_node} are coincident "
                    "(zero-length member)"
                )
            cx, cy, cz = dx / L, dy / L, dz / L
            # 3D transformation
            k_local = (E * A / L) * np.array(
                [
                    [1, -1],
                    [-1, 1],
                ]
            )
            transform = np.array(
                [
                    [cx, cy, cz, 0, 0, 0],
                    [0, 0, 0, cx, cy, cz],
                ]
            )
            k_global = transform.T @ k_local @ transform
            dof_map = [
                i_node * 3,
                i_node * 3 + 1,
                i_node * 3 + 2,
                j_node * 3,
                j_node * 3 + 1,
                j_node * 3 + 2,
            ]
        else:
            dx, dy = xj - xi, yj - yi
            # noqa: N806
            L = np.sqrt(dx**2 + dy**2)  # noqa: N806
            if L < 1e-12:
                raise ValueError(
                    f"Element {e_idx}: nodes {i_node} and {j_node} are coincident "
                    "(zero-length member)"
                )
            cx, cy = dx / L, dy / L
            # 2D transformation
            k_local = (E * A / L) * np.array(
                [
                    [1, -1],
                    [-1, 1],
                ]
            )
            transform = np.array(
                [
                    [cx, cy, 0, 0],
                    [0, 0, cx, cy],
                ]
            )
            k_global = transform.T @ k_local @ transform
            dof_map = [
                i_node * 2,
                i_node * 2 + 1,
                j_node * 2,
                j_node * 2 + 1,
            ]

        # Add to global stiffness
        for ii, gi in enumerate(dof_map):
            for jj, gj in enumerate(dof_map):
                K[gi, gj] += k_global[ii, jj]

        element_results.append(
            {
                "element": e_idx,
                "node_i": i_node,
                "node_j": j_node,
                "length_m": L,
                "area_m2": A,
                "youngs_modulus_pa": E,
                "axial_stiffness_n_m": E * A / L,
            }
        )

    # Apply loads
    for load in loads:
        node = load["node"]
        force = load["force"]
        if node < 0 or node >= n_nodes:
            raise ValueError(f"Load: invalid node index {node}")
        if len(force) != dim:
            raise ValueError(f"Load at node {node}: force must have {dim} components")
        for d in range(dim):
            F[node * dim + d] += force[d]

    # Keep the assembled (unpenalized) stiffness so support reactions can be recovered
    # correctly as R = K_orig @ U - F at the constrained DOFs. Computing reactions from
    # the penalty-augmented K instead only returns the solver residual (~0).
    K_orig = K.copy()  # noqa: N806

    # Apply constraints (penalty method)
    penalty = 1e12
    constrained_dofs = []
    for constraint in constraints:
        node = constraint["node"]
        fixed_dof = constraint["fixed_dof"]
        if node < 0 or node >= n_nodes:
            raise ValueError(f"Constraint: invalid node index {node}")
        for d in fixed_dof:
            if d < 0 or d >= dim:
                raise ValueError(f"Constraint at node {node}: invalid DOF {d}")
            gdof = node * dim + d
            K[gdof, gdof] += penalty
            constrained_dofs.append(gdof)

    # Solve K * U = F
    try:
        U = np.linalg.solve(K, F)  # noqa: N806
    except np.linalg.LinAlgError as exc:
        raise ValueError(
            "Stiffness matrix is singular. Check that constraints prevent rigid body motion."
        ) from exc

    # Compute reactions at constrained DOFs from the unpenalized stiffness.
    reactions = []
    reaction_forces = K_orig @ U - F
    for constraint in constraints:
        node = constraint["node"]
        fixed_dof = constraint["fixed_dof"]
        reaction = {"node": node, "reaction_force_n": [0.0] * dim}
        for d in fixed_dof:
            gdof = node * dim + d
            reaction["reaction_force_n"][d] = round(float(reaction_forces[gdof]), 4)
        reactions.append(reaction)

    # Compute member forces
    member_forces = []
    for e_idx, (elem, props) in enumerate(zip(elements, element_properties)):
        i_node, j_node = elem
        # noqa: N806
        E = props["youngs_modulus_pa"]  # noqa: N806
        # noqa: N806
        A = props["area_m2"]  # noqa: N806

        if dim == 3:
            xi, yi, zi = nodes[i_node]
            xj, yj, zj = nodes[j_node]
            dx, dy, dz = xj - xi, yj - yi, zj - zi
            L = np.sqrt(dx**2 + dy**2 + dz**2)  # noqa: N806
            cx, cy, cz = dx / L, dy / L, dz / L
            ui = U[i_node * 3 : i_node * 3 + 3]
            uj = U[j_node * 3 : j_node * 3 + 3]
            delta = (uj[0] - ui[0]) * cx + (uj[1] - ui[1]) * cy + (uj[2] - ui[2]) * cz
        else:
            xi, yi = nodes[i_node]
            xj, yj = nodes[j_node]
            dx, dy = xj - xi, yj - yi
            L = np.sqrt(dx**2 + dy**2)  # noqa: N806
            cx, cy = dx / L, dy / L
            ui = U[i_node * 2 : i_node * 2 + 2]
            uj = U[j_node * 2 : j_node * 2 + 2]
            delta = (uj[0] - ui[0]) * cx + (uj[1] - ui[1]) * cy

        force = (E * A / L) * delta
        stress = force / A

        member_forces.append(
            {
                "element": e_idx,
                "node_i": i_node,
                "node_j": j_node,
                "force_n": round(float(force), 4),
                "force_kn": round(float(force) / 1000, 6),
                "stress_pa": round(float(stress), 2),
                "stress_mpa": round(float(stress) / 1e6, 4),
                "state": "tension" if force > 0 else "compression" if force < 0 else "zero",
                "elongation_m": round(float(delta), 8),
            }
        )

    # Node displacements
    node_displacements = []
    for i in range(n_nodes):
        if dim == 3:
            disp = U[i * 3 : i * 3 + 3]
            node_displacements.append(
                {
                    "node": i,
                    "dx_m": round(float(disp[0]), 8),
                    "dy_m": round(float(disp[1]), 8),
                    "dz_m": round(float(disp[2]), 8),
                    "magnitude_m": round(
                        float(np.sqrt(disp[0] ** 2 + disp[1] ** 2 + disp[2] ** 2)), 8
                    ),
                }
            )
        else:
            disp = U[i * 2 : i * 2 + 2]
            node_displacements.append(
                {
                    "node": i,
                    "dx_m": round(float(disp[0]), 8),
                    "dy_m": round(float(disp[1]), 8),
                    "magnitude_m": round(float(np.sqrt(disp[0] ** 2 + disp[1] ** 2)), 8),
                }
            )

    return {
        "dimension": dim,
        "n_nodes": n_nodes,
        "n_elements": n_elements,
        "member_forces": member_forces,
        "node_displacements": node_displacements,
        "reactions": reactions,
    }
