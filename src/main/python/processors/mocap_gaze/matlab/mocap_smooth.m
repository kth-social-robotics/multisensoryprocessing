function Q=mocap_smooth(P, win, method)

  Q=NaN(size(P));
  for col=1:size(P,3)
    for coord=1:size(P,2)
      if sum(~isnan(P(:,coord,col)))>0
        Q(:,coord,col)=smooth(P(:,coord, col), win, method);
      end
    end
  end
