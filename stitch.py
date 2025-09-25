import fontforge
import math

def triangle_area(point1, point2, point3):
    """Area of a triangle."""
    x1, y1 = point1
    x2, y2 = point2
    x3, y3 = point3
    return 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    
def turning_amount(x1, y1, x2, y2, x3, y3, x4, y4):
    """How much you turn"""
    # Calculate direction vectors
    v1 = (x2 - x1, y2 - y1)  # Vector from (x1, y1) to (x2, y2)
    v2 = (x4 - x3, y4 - y3)  # Vector from (x3, y3) to (x4, y4)

    # Calculate dot product and magnitudes
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
    magnitude_v2 = math.sqrt(v2[0]**2 + v2[1]**2)

    # Calculate cosine of the angle
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        raise ValueError("Line segments must be non-zero length.")

    cos_theta = dot_product / (magnitude_v1 * magnitude_v2)

    # Clamp the value to the range [-1, 1] to avoid invalid inputs to acos
    cos_theta = max(-1.0, min(1.0, cos_theta))

    # Calculate the angle in radians
    angle = math.acos(cos_theta)

    # Calculate the cross product to determine the direction of the turn
    cross_product = v1[0] * v2[1] - v1[1] * v2[0]

    # Convert angle to degrees
    angle_degrees = math.degrees(angle)

    # Adjust the angle based on the direction of the cross product
    if cross_product < 0:
        angle_degrees = -angle_degrees

    return angle_degrees


def distancesq(point1, point2):
    """Calculate the Euclidean distance between two points squared."""
    return ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


def divide_segment(p0, p1, num_cuts):
    """Divide the segment between two points into equal parts."""
    if num_cuts != 1:
        return [
            (
                p0[0] + (p1[0] - p0[0]) * (i / num_cuts),
                p0[1] + (p1[1] - p0[1]) * (i / num_cuts)
            )
            for i in range(num_cuts + 1)
        ]

def distance_point_line(point, line_point1, line_point2):
    """Calculate the shortest distance from a point to a line defined by two points."""
    x0, y0 = point
    x1, y1 = line_point1
    x2, y2 = line_point2

    # Calculate the distance using the formula
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5

    return numerator / denominator


def are_collinear(point1, point2, point3, epsilon=1e-5):
    """Do not waste ink if the 3 points are collinear."""
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    x3, y3 = point3[0], point3[1]
    
    # Calculate the area (determinant)
    area = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
    
    # Check if the absolute area is less than the tolerance
    return abs(area) < epsilon

def convert_to_quadratic_and_generate_instructions(font_path, char, length=10, error_limit=3, div=1.3333):
    # Open the font
    font = fontforge.open(font_path)

    glyph = font[char]
        
    for contour in glyph.foreground:
        contour.is_quadratic = True
        
    glyph = font[char]

    glyph.simplify()
    glyph.simplify(error_limit)

    # Store string art instructions
    instructions = []

    # Iterate over each contour in the glyph
    for contour in glyph.foreground:
        points = []
        for point in contour:
            points.append(point)
        #points[:] = [ p for p in points if not p.interpolated ]
#        print(points)
        lastfalse = False
        p2 = []
        # remove duplicates (since we already converted it to quadratic, and consecutive points
        # not on curves must be duplicated).
        for p in points:
            if lastfalse and not p.on_curve:
                continue
            lastfalse = (not p.on_curve)
            p2.append(p)
#            print(p.on_curve)
        points = p2
        # Make sure there is a control point between every pair of True points
        p2 = []
        lasttrue = False
        lastpoint = None
        for p in points:
            if lasttrue and p.on_curve:
                p2.append(fontforge.point(((lastpoint.x+p.x)/2), ((lastpoint.y+p.y)/2), False))
            p2.append(p)
            lasttrue = p.on_curve
            lastpoint = p
        points = p2
#        print(points)
        # Put the first point into last
        if not points[0].on_curve:
            points.append(points[0])
            points = points[1:]
#        print(points)
        if points[-1].on_curve:
            points.append(fontforge.point((points[0].x+points[-1].x)/2,(points[0].y+points[-1].y)/2,False))
        points.append(points[0])
        curves = []
        for i in range(0,len(points)-2,2):
            curves.append(((points[i].x,points[i].y),(points[i+1].x,points[i+1].y),(points[i+2].x,points[i+2].y)))
        # Generate stitching instructions for quadratic curves
#        print(curves)
        for i in range(len(curves)):
            p0, p1 = curves[i][0], curves[i][2]
            control_point = curves[i][1]
            if are_collinear(p0, p1, control_point):
                instructions.append(((p0[0],p0[1]),(p1[0],p1[1])))
                continue

            num_cuts = max(1,int((math.sqrt(abs(triangle_area(p0, p1, control_point)))/length*distance_point_line(control_point, p0,p1)/math.sqrt(distancesq(p0,p1))*2+30*math.sqrt(360-turning_amount(p0[0],p0[1],control_point[0],control_point[1],control_point[0],control_point[1],p1[0],p1[1]))*math.sqrt(math.sqrt(distancesq(p0,p1)))/2000+math.sqrt(distancesq(p0,p1))/330)/div))
#            num_cuts = max(1,int((1/math.sqrt((1/distancesq(p0,control_point)+1/distancesq(control_point,p1))/2))/length))
            if num_cuts == 1:
                instructions.append(((p0[0],p0[1]),(p1[0],p1[1])))
                continue
            if (triangle_area(p0, p1, control_point)/math.sqrt(distancesq(p0,p1)) <= 5):
                instructions.append(((p0[0],p0[1]),(p1[0],p1[1])))
                continue
            # Divide the segments
            a_points = divide_segment(p0, control_point, num_cuts)  # Points on P0P1
            b_points = divide_segment(control_point, p1, num_cuts)  # Points on P1P2
            # Stitch points
            for j in range(num_cuts + 1):
                a_point = a_points[j]  # Point on P0P1
                b_point = b_points[j]  # Point on P1P2
                if j % 2 == 0:
                    instructions.append(((b_point[0],b_point[1]),(a_point[0],a_point[1])))
                else:
                    instructions.append(((a_point[0],a_point[1]),(b_point[0],b_point[1])))
        instructions.append("New")
    font.generate('test.ttf')
    # Close the font
    font.close()

    return instructions

if __name__ == "__main__":
    # Input font path and character from stdin
    font_path = input("Enter the font path: ")  # Prompt for font path
    character = input("Enter the character: ")   # Prompt for character

    # Generate stitching instructions
    instructions = convert_to_quadratic_and_generate_instructions(font_path, character)

    round_digits = 3
    # Print the instructions
    noextrasins = [(((round(ins[0][0],round_digits),round(ins[0][1],round_digits)),
                     (round(ins[1][0],round_digits),round(ins[1][1],round_digits)))) for ins in instructions if ins != "New"]
#    print(noextrasins)
    
    s = set()
    for ins in noextrasins:
        s.add(ins[0])
        s.add(ins[1])
    
    dct = {value: index for index, value in enumerate(list(s))}
    
    ins_numbered = []
    for ins in instructions:
        if ins == "New":
            ins_numbered.append(ins)
        else:
            ins = (((round(ins[0][0],round_digits),round(ins[0][1],round_digits)),
                    (round(ins[1][0],round_digits),round(ins[1][1],round_digits))))
            ins_numbered.append((dct[ins[0]],dct[ins[1]]))
    
    print(dct)
    print(ins_numbered)
    
    # LaTeX
    with open('table.tex', 'w') as f:
        f.write(r'\documentclass{article}\usepackage[margin=1cm]{geometry}\usepackage{multicol}\begin{document}\footnotesize')
        f.write(r'\begin{multicols}{5}\noindent ')
        for ins in ins_numbered:
            if ins != "New":
                f.write(f'{ins[0]} To: {ins[1]}' + r'\\')
            else:
                f.write(r'---\/---\/---\\')
        f.write(r'All Done!\end{multicols}\end{document}')
