function [ P ] = matrix2points(Y)
%matrix2points Reshapes 3D point data matrix
%   INPUT: Y (N x 3*M)
%   OUTPUT P (N,3,M)
    N = size(Y,1);
    M = floor(size(Y,2)/3);
    P = reshape(Y, N, 3, M);
end

