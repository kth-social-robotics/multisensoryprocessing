function [ P ] = clamp_magnitude(P, min, max)
%Clamps a vector to a be within given distances. 
    for mi = 1:size(P,3)
        dist = calc_norm(P(:,:,mi));
        bin = dist>max;
        P(bin,:,mi) = calc_unit(P(bin,:,mi))*max;
        bin = dist<min;
        P(bin,:,mi) = calc_unit(P(bin,:,mi))*min;
    end
end

