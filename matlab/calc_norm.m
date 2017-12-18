function N = calc_norm( A )
% Summary of this function goes here
% Detailed explanation goes here


N=zeros(size(A,1),size(A,3));

for col=1:size(A,3)
    A2 = A(:,:,col).^2;
    N(:,col) = sqrt(sum(A2,2));
end

