import math

def compute_dist_btw_2points(A, B, precision=1):
    """
    Compute distances between two points
    Inputs: (x,y)
    """
    # Retrieve variables
    xa = A[0]; ya = A[1]
    xb = B[0]; yb = B[1]

    # Compute segment' size
    AB = math.sqrt((xb - xa)**2 + (yb - ya)**2)
    
    return round(AB, precision)


def get_angle(A, B, CAD):
    """
    Return the relative angle between
    two points, given their absolute position and
    the absolute angle of point A with the EAST at 0
    """
    # Construct a right rectangle ACB
    # - Locate point C (ya, xb)
    C = (A[1], B[0])

    # Measure segments AC and BC
    AC = compute_dist_btw_2points(A, C)
    BC = compute_dist_btw_2points(B, C)

    # Use trigo rule sin x = opposed/adjacent
    # to get angle x (ABC)
    ABC = math.degrees(math.atan(AC/BC))

    # Deduce angle (BAC)
    BAC = 180 - 90 - ABC

    # Deduce angle BAD
    BAD = CAD - BAC

    return BAD

# test: should yield 25 degrees
A = (11343, 6137)
B = (14517, 7786)
CAD = 25
BAD = get_angle(A, B, CAD)
print("obtained", BAD)
print("expected", CAD)


# Which angle ?
A = (9954, 4526)
B = (14517, 7786)
CAD = 85
BAD = get_angle(A, B, CAD)
print(BAD)