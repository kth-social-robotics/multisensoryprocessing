function [P,L] = extract_all_rigidbodymarkers(CSVDATA, labels, types)
    % extract labeled marker data from cvs data structure
    markers_bin = strcmp(types, 'Rigid Body Marker');
    uqlbls = unique(labels(markers_bin));
    P=nan(size(CSVDATA,1), 3, length(uqlbls));
    for i =1:length(uqlbls)
        tmp = CSVDATA(:,strcmp(labels, uqlbls{i}));
        P(:,:,i) = tmp(:,1:3);
    end    
    L = uqlbls';
