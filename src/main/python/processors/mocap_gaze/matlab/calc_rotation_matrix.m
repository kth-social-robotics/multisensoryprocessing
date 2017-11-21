function R = calc_rotation_matrix(dir1, dir2)

  e1 = calc_unit(dir1);
  e3 = calc_unit(cross(e1, dir2));
  e2 = cross(e3, e1);

  R =  [e1' e2' e3'];
end
