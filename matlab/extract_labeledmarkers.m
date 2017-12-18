function [P,L] = extract_labeledmarkers(CSVDATA, labels, types)
    % extract labeled marker data from cvs data structure
    unlabeled_bin = strncmp(labels ,'Unlabeled',9);
    markers_bin = strcmp(types, 'Marker');
    uqlbls = unique(labels(~unlabeled_bin&markers_bin));
    P = extract_markerdata(CSVDATA, labels, types, uqlbls);
    L = uqlbls';