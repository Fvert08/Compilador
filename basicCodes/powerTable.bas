 10 REM POWER TABLE
 11 DATA 8, 4
 15 READ N0 , P0
 20 PRINT "n"
 25 FOR P = 2 TO P0 
 30   PRINT "n ^" , P
 35 NEXT P
 40 PRINT "sum of powers"
 45 LET S = 0
 50 FOR N = 2 TO N0
 55   PRINT N
 60   FOR P = 2 TO P0
 61     LET K = N ^ P
 65     LET S = S + K
 70     PRINT N ^ P
 75   NEXT P
 80   PRINT S
 85 NEXT N
 99 END
