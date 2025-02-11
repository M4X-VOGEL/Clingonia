% assignment predicates
% start(ID, (X,Y), EarliestDeparture, Direction)
% end(ID, (X,Y), LatestArrival)
% cell((X,Y), Track)

% custom predicates
% action(train(ID), Action, Timestep)
% position(ID, (X,Y), Direction, Timestep)
% trans(TrackID, IncomingDirection, OutgoingDirection, Move)
% firstAction(ID, Timestep)



% valid moves
move(move_forward).
move(move_left).
move(move_right).
move(wait).


% actions

% Generate actions for path
{ action(train(ID), M, T) : move(M), T = (ED-1)..LA } N :- start(ID, _, ED, _),  end(ID, _, LA), N=LA-(ED-1).

% first action
firstAction(ID, T) :- action(train(ID), _, T), not action(train(ID), _, T-1).

% ensure no unexpected timestep gaps in list of actions
:- action(train(ID), _, T1), action(train(ID), _, T3), T3 = T1 + 2, not action(train(ID), _, T1+1).



% deduce positions from actions

% start if earliest departure is 0
position(ID, (X,Y), D, TGo) :- start(ID, (X,Y), 0, D), action(train(ID), move_forward, TSpawn), firstAction(ID, TSpawn), TSpawn>=0, TGo=TSpawn+1.

% start if earliest departure > 0
position(ID, (X,Y), D, TGo) :- start(ID, (X,Y), ED, D), action(train(ID), move_forward, TSpawn), firstAction(ID, TSpawn), TSpawn>=(ED-1), TGo=TSpawn+1, ED>0.

% waits
position(ID, (X,Y), D, TN) :- position(ID, (X,Y), D, TO), action(train(ID), wait, TO) , TN = TO+1.

% straights
position(ID, (XN,YN), n, TN) :- position(ID, (XO,YO), n, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, n, n, move_forward), XN=XO-1, YN=YO, TN=TO+1.
position(ID, (XN,YN), e, TN) :- position(ID, (XO,YO), e, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, e, e, move_forward), XN=XO, YN=YO+1, TN=TO+1.
position(ID, (XN,YN), s, TN) :- position(ID, (XO,YO), s, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, s, s, move_forward), XN=XO+1, YN=YO, TN=TO+1.
position(ID, (XN,YN), w, TN) :- position(ID, (XO,YO), w, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, w, w, move_forward), XN=XO, YN=YO-1, TN=TO+1.

% curves
position(ID, (XN,YN), e, TN) :- position(ID, (XO,YO), n, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, n, e, move_forward), XN=XO, YN=YO+1, TN=TO+1.
position(ID, (XN,YN), w, TN) :- position(ID, (XO,YO), n, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, n, w, move_forward), XN=XO, YN=YO-1, TN=TO+1.
position(ID, (XN,YN), n, TN) :- position(ID, (XO,YO), e, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, e, n, move_forward), XN=XO-1, YN=YO, TN=TO+1.
position(ID, (XN,YN), s, TN) :- position(ID, (XO,YO), e, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, e, s, move_forward), XN=XO+1, YN=YO, TN=TO+1.
position(ID, (XN,YN), e, TN) :- position(ID, (XO,YO), s, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, s, e, move_forward), XN=XO, YN=YO+1, TN=TO+1.
position(ID, (XN,YN), w, TN) :- position(ID, (XO,YO), s, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, s, w, move_forward), XN=XO, YN=YO-1, TN=TO+1.
position(ID, (XN,YN), n, TN) :- position(ID, (XO,YO), w, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, w, n, move_forward), XN=XO-1, YN=YO, TN=TO+1.
position(ID, (XN,YN), s, TN) :- position(ID, (XO,YO), w, TO), action(train(ID), move_forward, TO), cell((XO,YO), TID), trans(TID, w, s, move_forward), XN=XO+1, YN=YO, TN=TO+1.

% left turns
position(ID, (XN,YN), w, TN) :- position(ID, (XO,YO), n, TO), action(train(ID), move_left, TO), cell((XO,YO), TID), trans(TID, n, w, move_left), XN=XO, YN=YO-1, TN=TO+1.
position(ID, (XN,YN), n, TN) :- position(ID, (XO,YO), e, TO), action(train(ID), move_left, TO), cell((XO,YO), TID), trans(TID, e, n, move_left), XN=XO-1, YN=YO, TN=TO+1.
position(ID, (XN,YN), e, TN) :- position(ID, (XO,YO), s, TO), action(train(ID), move_left, TO), cell((XO,YO), TID), trans(TID, s, e, move_left), XN=XO, YN=YO+1, TN=TO+1.
position(ID, (XN,YN), s, TN) :- position(ID, (XO,YO), w, TO), action(train(ID), move_left, TO), cell((XO,YO), TID), trans(TID, w, s, move_left), XN=XO+1, YN=YO, TN=TO+1.

% right turns
position(ID, (XN,YN), e, TN) :- position(ID, (XO,YO), n, TO), action(train(ID), move_right, TO), cell((XO,YO), TID), trans(TID, n, e, move_right), XN=XO, YN=YO+1, TN=TO+1.
position(ID, (XN,YN), s, TN) :- position(ID, (XO,YO), e, TO), action(train(ID), move_right, TO), cell((XO,YO), TID), trans(TID, e, s, move_right), XN=XO+1, YN=YO, TN=TO+1.
position(ID, (XN,YN), w, TN) :- position(ID, (XO,YO), s, TO), action(train(ID), move_right, TO), cell((XO,YO), TID), trans(TID, s, w, move_right), XN=XO, YN=YO-1, TN=TO+1.
position(ID, (XN,YN), n, TN) :- position(ID, (XO,YO), w, TO), action(train(ID), move_right, TO), cell((XO,YO), TID), trans(TID, w, n, move_right), XN=XO-1, YN=YO, TN=TO+1.



% constraints

% train reaches endpoint
:- end(ID, (X,Y), _), not position(ID, (X,Y), _, _).

% no position after latest arrival
:- end(ID, _, LA), position(ID, _, _,T), T>LA.

% no position after reaching endpoint
:- end(ID, (X,Y), _), position(ID, (X,Y), _, TA), position(ID, _, _, TB), TB>TA.

% unique actions and positions at every time step
:- action(train(ID), MA, T), action(train(ID), MB, T), MA != MB.
:- position(ID, (XA, YA), D, T), position(ID, (XB, YB), D, T), XA != XB.
:- position(ID, (XA, YA), D, T), position(ID, (XB, YB), D, T), YA != YB.

% train makes valid transition on non-wait move
:- position(ID, (X,Y), D, T), cell((X,Y), TID), not trans(TID, D, _, M), action(train(ID), M, T), not M = wait.

% multiple trains cannot occupy same position at same time
:- position(IDA, (X,Y), _, T), position(IDB, (X,Y), _, T), IDA != IDB.

% two trains cannot swap positions
:- position(IDA, (XA,YA), _, TA), position(IDB, (XB,YB), _, TA), position(IDA, (XB,YB), _, TB), position(IDB, (XA,YA), _, TB), IDA != IDB, TB=TA+1.



% optimizations

% minimize number of actions
#minimize { 1 : action(train(ID), _, _) }.
#minimize { 1 : action(_, wait, _) }.
#minimize { 1 : action(_, move_forward, _) }.
#minimize { T : action(_, _, T) }.



% output
#show action/3.
