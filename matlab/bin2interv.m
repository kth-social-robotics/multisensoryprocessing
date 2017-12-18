function INTERV= bin2interv(BIN)
% converts a binary data column to a set of intervals
% ex: BIN = [1 1 1 0 0 0 1 1 1 0 0 0]' => [1 3; 7 9]

    [starts, ends, cnt] = create_intervals(find(BIN), 1);
    INTERV = [starts ends];
end

