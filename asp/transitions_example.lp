% Format:
% trans(TrackID, Facing , Direction, Move)
% trans(TrackID, ComingFrom, GoingTO, Move)


% Track Type #1

% straights
trans(32800, s, s, move_forward).
trans(32800, n, n, move_forward).
trans(1025, e, e, move_forward).
trans(1025, w, w, move_forward).

% curves
trans(4608, e, s, move_forward).
trans(4608, n, w, move_forward).

trans(16386, n, e, move_forward).
trans(16386, w, s, move_forward).

trans(72, s, e, move_forward).
trans(72, w, n, move_forward).

trans(2064, e, n, move_forward).
trans(2064, s, w, move_forward).



% Track Type #2

% left hand switches
trans(37408, s, s, move_forward).
trans(37408, n, n, move_forward).
trans(37408, n, w, move_left).
trans(37408, e, s, move_forward).

trans(17411, e, e, move_forward).
trans(17411, w, w, move_forward).
trans(17411, n, e, move_forward).
trans(17411, w, s, move_left).

trans(32872, s, s, move_forward).
trans(32872, n, n, move_forward).
trans(32872, s, e, move_left).
trans(32872, w, n, move_forward).

trans(3089, w, w, move_forward).
trans(3089, e, e, move_forward).
trans(3089, e, n, move_left).
trans(3089, s, w, move_forward).

% right hand switches
trans(49186, n, n, move_forward).
trans(49186, s, s, move_forward).
trans(49186, n, e, move_right).
trans(49186, w, s, move_forward).

trans(1097, e, e, move_forward).
trans(1097, w, w, move_forward).
trans(1097, s, e, move_forward).
trans(1097, w, n, move_right).

trans(34864, s, s, move_forward).
trans(34864, n, n, move_forward).
trans(34864, s, w, move_right).
trans(34864, e, n, move_forward).

trans(5633, w, w, move_forward).
trans(5633, e, e, move_forward).
trans(5633, e, s, move_right).
trans(5633, n, w, move_forward).



% Track Type #3
trans(33825, s, s, move_forward).
trans(33825, n, n, move_forward).
trans(33825, e, e, move_forward).
trans(33825, w, w, move_forward).



% Track Type #4
trans(38433, n, n, move_forward).
trans(38433, s, s, move_forward).
trans(38433, e, e, move_forward).
trans(38433, w, w, move_forward).
trans(38433, e, s, move_right).
trans(38433, n, w, move_left).

trans(50211, n, n, move_forward).
trans(50211, s, s, move_forward).
trans(50211, e, e, move_forward).
trans(50211, w, w, move_forward).
trans(50211, n, e, move_right).
trans(50211, w, s, move_left).

trans(33897, n, n, move_forward).
trans(33897, s, s, move_forward).
trans(33897, e, e, move_forward).
trans(33897, w, w, move_forward).
trans(33897, s, e, move_left).
trans(33897, w, n, move_right).

trans(35889, n, n, move_forward).
trans(35889, s, s, move_forward).
trans(35889, e, e, move_forward).
trans(35889, w, w, move_forward).
trans(35889, e, n, move_left).
trans(35889, s, w, move_right).



% Track Type #5
trans(38505, n, n, move_forward).
trans(38505, s, s, move_forward).
trans(38505, e, e, move_forward).
trans(38505, w, w, move_forward).
trans(38505, s, e, move_left).
trans(38505, w, n, move_right).
trans(38505, e, s, move_right).
trans(38505, n, w, move_left).

trans(52275, n, n, move_forward).
trans(52275, s, s, move_forward).
trans(52275, e, e, move_forward).
trans(52275, w, w, move_forward).
trans(52275, s, w, move_right).
trans(52275, e, n, move_left).
trans(52275, w, s, move_left).
trans(52275, n, e, move_right).



% Track Type #6
trans(20994, n, e, move_right).
trans(20994, n, w, move_left).
trans(20994, e, s, move_forward).
trans(20994, w, s, move_forward).

trans(16458, w, n, move_right).
trans(16458, w, s, move_left).
trans(16458, n, e, move_forward).
trans(16458, s, e, move_forward).

trans(2136, s, e, move_left).
trans(2136, s, w, move_right).
trans(2136, w, n, move_forward).
trans(2136, e, n, move_forward).

trans(6672, e, s, move_right).
trans(6672, e, n, move_left).
trans(6672, s, w, move_forward).
trans(6672, n, w, move_forward).
