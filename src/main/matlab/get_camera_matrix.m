function [P, K, R, T] = get_camera_matrix(x, X)
    % calculates the camera matrix given pairs of screen and world
    % coordinates. See 
    % input:    x - screen coordinates (2xN)
    %           X - world coordinates (3xN)
    % output:   P - camera projection matrix
    %           R - rotation matrix
    %           K - field of view (?)
    %           T - translation
    x = [x;ones(1,size(x,2))];
    X = [X;ones(1,size(X,2))];
%    com = mean(x,2);
%     s=0.001;
%     N=[s 0 -s*com(1);0 s -s*com(2);0 0 1];
%     x = N * x;  
    A = get_A(x, X);    
    [U S V] = svd(A);
%    P = V(:, 1);
    P = V(:, size(V,2));
    P = reshape(P, 4, 3)';
    
    AA = P(1:3, 1:3);
    A1T = AA(1,:);
    A2T = AA(2,:);
    A3T = AA(3,:);
    f = norm(A3T);
    R3T = 1/f*A3T;
    e = A2T*R3T';
    dR2T = A2T - e*R3T;
    d = norm(dR2T);
    R2T = 1/d*dR2T;
    b = A1T * R2T';
    c = A1T * R3T';
    aR1T = A1T - b * R2T - c * R3T;
    a = norm(aR1T);
    R1T = 1/a * aR1T;
    K = [a b c; 0 d e; 0 0 f]/f;
    R = [R1T' R2T' R3T'];
    T = -R*K\P(:,4)/f;
%     sign = det(R);
%     R = R * sign;
%    T = -sign*R*K\P(:,4)/f;
%     K = N\K;
return