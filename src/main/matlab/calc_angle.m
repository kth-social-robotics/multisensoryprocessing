function [ ang ] = calc_angle( r1, r2)

    length1 = sqrt(sum(r1.^2,2));
    length2 = sqrt(sum(r2.^2,2));
    dotprod = dot(r1,r2,2);
    ang = acos(dotprod./(length1.*length2));        
end
