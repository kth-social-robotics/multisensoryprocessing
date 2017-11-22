function U = calc_unit( A )
% Summary of this function goes here
% Detailed explanation goes here


N=zeros(size(A,1),size(A,3));
U=zeros(size(A));
for col=1:size(A,3)
    A2 = A(:,:,col).^2;
    N(:,col) = sqrt(sum(A2,2));
    U = A(:,:,col)./[N N N];
end

