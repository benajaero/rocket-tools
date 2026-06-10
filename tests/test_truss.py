"""Tests for truss analysis using the direct stiffness method."""

import pytest

from rocket_tools.structural.truss import truss_analysis


class TestTruss2D:
    def test_simple_2bar_truss(self):
        """Two-bar truss: node 0 fixed, node 1 loaded vertically."""
        result = truss_analysis(
            nodes=[[0.0, 0.0], [1.0, 0.0], [0.5, 0.866]],
            elements=[[0, 2], [1, 2]],
            element_properties=[
                {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
                {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
            ],
            constraints=[
                {"node": 0, "fixed_dof": [0, 1]},
                {"node": 1, "fixed_dof": [0, 1]},
            ],
            loads=[
                {"node": 2, "force": [0.0, -10000.0]},
            ],
        )
        assert result["dimension"] == 2
        assert result["n_nodes"] == 3
        assert result["n_elements"] == 2
        assert len(result["member_forces"]) == 2
        assert len(result["node_displacements"]) == 3
        # Node 2 should displace downward
        assert result["node_displacements"][2]["dy_m"] < 0
        # Both members in compression (supporting downward load from above)
        for mf in result["member_forces"]:
            assert mf["state"] == "compression"

    def test_3bar_symmetric_truss(self):
        """Symmetric 3-bar truss with center load."""
        result = truss_analysis(
            nodes=[[0.0, 0.0], [2.0, 0.0], [1.0, 1.0]],
            elements=[[0, 2], [1, 2], [0, 1]],
            element_properties=[
                {"youngs_modulus_pa": 70e9, "area_m2": 0.0005},
                {"youngs_modulus_pa": 70e9, "area_m2": 0.0005},
                {"youngs_modulus_pa": 70e9, "area_m2": 0.0005},
            ],
            constraints=[
                {"node": 0, "fixed_dof": [0, 1]},
                {"node": 1, "fixed_dof": [1]},
            ],
            loads=[
                {"node": 2, "force": [0.0, -5000.0]},
            ],
        )
        assert result["n_elements"] == 3
        # Check reactions exist
        assert len(result["reactions"]) > 0

    def test_invalid_node_index(self):
        with pytest.raises(ValueError, match="invalid node index"):
            truss_analysis(
                nodes=[[0.0, 0.0], [1.0, 0.0]],
                elements=[[0, 5]],  # Node 5 doesn't exist
                element_properties=[{"youngs_modulus_pa": 200e9, "area_m2": 0.001}],
                constraints=[{"node": 0, "fixed_dof": [0, 1]}],
                loads=[],
            )

    def test_singular_stiffness(self):
        with pytest.raises(ValueError, match="singular"):
            truss_analysis(
                nodes=[[0.0, 0.0], [1.0, 0.0]],
                elements=[[0, 1]],
                element_properties=[{"youngs_modulus_pa": 200e9, "area_m2": 0.001}],
                constraints=[],  # No constraints = rigid body motion
                loads=[{"node": 1, "force": [1000.0, 0.0]}],
            )

    def test_zero_load(self):
        """Truss with no loads should have zero displacement."""
        result = truss_analysis(
            nodes=[[0.0, 0.0], [1.0, 0.0], [0.5, 0.866]],
            elements=[[0, 2], [1, 2]],
            element_properties=[
                {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
                {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
            ],
            constraints=[
                {"node": 0, "fixed_dof": [0, 1]},
                {"node": 1, "fixed_dof": [0, 1]},
            ],
            loads=[],
        )
        for disp in result["node_displacements"]:
            assert abs(disp["magnitude_m"]) < 1e-10


class TestTruss3D:
    def test_simple_3d_tower(self):
        """Simple 3D tower with base fixed and top loaded."""
        result = truss_analysis(
            nodes=[
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.5, 0.5, 2.0],
            ],
            elements=[
                [0, 4], [1, 4], [2, 4], [3, 4],
            ],
            element_properties=[
                {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
                {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
                {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
                {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
            ],
            constraints=[
                {"node": 0, "fixed_dof": [0, 1, 2]},
                {"node": 1, "fixed_dof": [0, 1, 2]},
                {"node": 2, "fixed_dof": [0, 1, 2]},
                {"node": 3, "fixed_dof": [0, 1, 2]},
            ],
            loads=[
                {"node": 4, "force": [0.0, 0.0, -50000.0]},
            ],
        )
        assert result["dimension"] == 3
        assert result["n_nodes"] == 5
        assert result["n_elements"] == 4
        # Top node should displace downward
        assert result["node_displacements"][4]["dz_m"] < 0
        # All members in compression (pushing up on the loaded top node)
        for mf in result["member_forces"]:
            assert mf["state"] == "compression"

    def test_mismatched_dimensions(self):
        with pytest.raises(ValueError, match="expected 2"):
            truss_analysis(
                nodes=[[0.0, 0.0], [1.0, 0.0, 0.0]],  # Mixed 2D/3D
                elements=[[0, 1]],
                element_properties=[{"youngs_modulus_pa": 200e9, "area_m2": 0.001}],
                constraints=[{"node": 0, "fixed_dof": [0, 1]}],
                loads=[],
            )
