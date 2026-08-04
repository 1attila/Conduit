from mconduit.utils import coords
from mconduit import Vec3d


def test_approx_fix():

    assert coords.approx_fix(Vec3d(10.5, 1.4, 0.2)) == Vec3d(10.5, 1.4, 0.2) # No changes
    assert coords.approx_fix(Vec3d(-10, 0, -3)) == Vec3d(-10, 0, -3) # No changes
    assert coords.approx_fix(Vec3d(-10.5, -10.5, -11.2)) == Vec3d(-11.0, -10.5, -11.2) # Only x
    assert coords.approx_fix(Vec3d(-15.2, -5.3, 10.7)) == Vec3d(-15.2, -5.3, 10.7) # No changes
    assert coords.approx_fix(Vec3d(-25.7, 0, 13)) == Vec3d(-26.2, 0, 13) # Only x
    assert coords.approx_fix(Vec3d(-32.4, 11, -2.9)) == Vec3d(-32.4, 11, -3.4) # Only z
    assert coords.approx_fix(Vec3d(-12.8, -2.7, -18.9)) == Vec3d(-13.3, -2.7, -19.4) # Both x and z
    

def test_ow_to_nether():

    assert coords.ow_to_nether(Vec3d(17, 102, -15)) == Vec3d(2, 12, -2)


def test_chunk_coords():
    
    assert coords.chunk_coords(Vec3d(20, 0, -100)) == Vec3d(1, 0, -7)
    

def test_chunk_to_region():
    
    assert coords.chunk_to_region(-150, 2762) == (-5, 86)

    
def test_iter_coord():
    
    assert list(coords.iter_coord(10, 10)) == [10]
    assert list(coords.iter_coord(-1, 1)) == [-1, 0, 1]
    assert list(coords.iter_coord(1, -1)) == [1, 0, -1]
    assert list(coords.iter_coord(10, 8)) == [10, 9, 8]
    assert list(coords.iter_coord(-10, -8)) == [-10, -9, -8]