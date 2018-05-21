extensions [csv]

breed [pools pool]

breed [investors investor]

pools-own [
  pool-number            ;; Distinguish each pool from the others
  max-payoff             ;; Amount to be distributed if there is any payout
  probability-payoff     ;; Probability of this pool paying out
  payoffs                ;; List of payoffs from pool
                         ;; sorted, latest first
  numbers                ;; List of number of investors in pool
                         ;; sorted, latest first
  total-payoff           ;; Total paid by this pool to date
  potential-payoff       ;; Total that could have been paid out.
                         ;; For low and high pools, this is the
                         ;; same as total-payoff. For the stable pool
                         ;; it is the payout assuming everyone is in
                         ;; this pool. Compare with total-payoff
                         ;; to calculate the amount that has been foregone
                         ;; by using risky pools
]

investors-own [
  wealth                 ;; Total payoff accumulated to date
  predictors             ;; The predcits available for forcasting
  my-payoffs             ;; List off payoffs received (not allowing for tau), in reverse chronological order
  my-choices             ;; List of pools chosen to date, in reverse chronological order
  sum-squares-error      ;; Error from predictors to date
  strategy-index         ;; Indicates which strategy was used
]

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; When Setup button pressed, paint patches blue, and create the pools and investors

to setup
  clear-all
  ask patches [set pcolor blue]
  let next-pool 0
  create-ordered-pools 3 [
    initialize-pool next-pool
    set next-pool next-pool + 1
  ]

  let n-experiencers int (p-experiencers * n-investors)
  let radius-inner-circle ifelse-value (n-cartel = 0) [9][6]
  let radius-outer-circle ifelse-value (n-cartel = 0) [18][12]
  let radius-cartel 20
  create-ordered-investors  n-investors - n-experiencers - n-cartel [
    initialize-investor "fish" radius-outer-circle (map [-> linear-predictor INIT [] [] [] [] [] ] range n-predictors) False
  ]

  create-ordered-investors  n-experiencers [
    initialize-investor "fish 2" radius-inner-circle (list [[func a b c d] -> experience-predictor func a b c d [[x y]-> simple-coarse-grainer3 x y]]) False
  ]

  create-ordered-investors n-cartel[
    initialize-investor "shark" radius-cartel (list [[func a b c d] -> cartel-predictor func a b c d ]) True
  ]

  reset-ticks
end

;; Setup properties for one  pool
to initialize-pool [next-pool]
  fd 1
  set shape "face neutral"
  set pool-number next-pool
  if pool-number = POOL-STABLE [set-pool-characteristics green 1 1]
  if pool-number = POOL-LOW    [set-pool-characteristics yellow max-payoff-low p-payoff-low]
  if pool-number = POOL-HIGH   [set-pool-characteristics red max-payoff-high p-payoff-high]
  set payoffs []
  set numbers []
  set total-payoff 0
end

;; Setup those variables that ditinguish one pool from another
to set-pool-characteristics [colour payoff p-payoff]
  set color colour
  set max-payoff max-payoff-high
  set probability-payoff p-payoff-high
end

;; Setup properties for one investor, and assign to a random pool
to initialize-investor [myshape myradius mypredictors is-cartel]
  set wealth 0
  set my-payoffs []
  let pool-index ifelse-value is-cartel [POOL-HIGH][(1 + random-tower (list p-start-low p-start-high)) mod 3]
  create-link-with one-of pools with [pool-number = pool-index]
  set my-choices (list pool-index)
  set shape myshape
  fd myradius
  set predictors mypredictors
  set strategy-index  (runresult (first predictors) ID [] [] [] [])

  colourize
end


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
to go
  ;; Historical data, which will be loaded from corresponding pools
  let low-payoff []
  let high-payoff []
  let low-number []
  let high-number []
  let low-return 0
  let high-return 0

  ask pools [
    ;; Decide whther to pay
    let selection random-float 1
    let mypayoff ifelse-value (selection < probability-payoff) [max-payoff][0]
    set shape ifelse-value (selection < probability-payoff) ["face happy"]["face sad"]

    ;; Apportion payout between subscribers
    let n-members count link-neighbors
    if n-members > 0 and probability-payoff < 1 [set mypayoff mypayoff / n-members]
    set numbers fput n-members numbers
    set payoffs fput mypayoff payoffs

    if pool-number = POOL-LOW [
      set low-payoff  payoffs
      set low-number numbers
      set low-return estimate-return payoffs numbers
    ]
    if pool-number = POOL-HIGH [
      set high-payoff  payoffs
      set high-number numbers
      set high-return estimate-return payoffs numbers
    ]
    set total-payoff total-payoff + mypayoff * n-members
    set potential-payoff ifelse-value(pool-number = POOL-STABLE) [
      potential-payoff + mypayoff * n-investors
    ][
      total-payoff
    ]
  ]

  ;; Use links to find out how much current pool will pay each investor
  ask investors [
    let delta-wealth 0
    ask one-of in-link-neighbors [set delta-wealth first payoffs]
    set wealth wealth + delta-wealth
    set my-payoffs fput delta-wealth my-payoffs
  ]

  ask investors [resize]

  if ticks >  n-ticks [stop]

  ask investors [  ;; Select best pool
    ifelse g-random-jump [
      let recommended-pool (1 + random-tower (list p-start-low p-start-high)) mod 3
      let current-pool first my-choices
      ifelse recommended-pool = current-pool [
        set my-choices fput recommended-pool my-choices
      ][
        set wealth wealth - tau
        set my-choices fput recommended-pool my-choices
        ask one-of my-out-links [die]
        create-link-with one-of pools with [pool-number = recommended-pool]
        colourize
      ]
    ][
      let predicted-returns (runresult (first predictors) PREDICT low-payoff high-payoff low-number high-number)
      let current-pool first my-choices
      let revised-prediction (map [[element i] -> ifelse-value (i = current-pool) [element][max (list 0 (element - tau-weight * tau))]] predicted-returns range 3)
      let recommended-return max revised-prediction
      let predicted-benefit recommended-return - item current-pool revised-prediction

      let recommended-pool 0
      ifelse randomize-step [
        let r random-float sum (revised-prediction)
        if r > first revised-prediction [set recommended-pool ifelse-value ( r < (item 1 revised-prediction) + (first revised-prediction))[1][2]   ]
      ][
        if recommended-return = item 1 revised-prediction [set recommended-pool 1]
        if recommended-return = item 2 revised-prediction [set recommended-pool 2]
      ]
      ;; If pool different, consider whether to change (tau)
      ifelse recommended-pool = current-pool [
        set my-choices fput recommended-pool my-choices
      ][
        ifelse advice-is-credible recommended-pool predicted-benefit [
          set wealth wealth - tau
          set my-choices fput recommended-pool my-choices
          ask one-of my-out-links [die]
          create-link-with one-of pools with [pool-number = recommended-pool]
          colourize
        ][
          set my-choices fput current-pool my-choices
        ]
      ]
    ]

  ]

  ;; Breed predictors

  ask investors [
    let offspring map [predictor -> (runresult predictor CLONE low-payoff high-payoff low-number high-number)] predictors
    if is-anonymous-reporter? first offspring  [set predictors sentence predictors offspring]
  ]

  ;; Select best predictors for next iteration

  ask investors [
    if length predictors > 1[  ;;FIXME
      let indices range length predictors
      let scores-with-indices (map [[predictor index] -> (list (runresult predictor EVALUATE low-payoff high-payoff low-number high-number) index) ] predictors indices)
      let scores-sorted-with-indices sort-by [[l1 l2]-> first l1 < first l2] scores-with-indices  ;; sort by evaulation score
      set sum-squares-error first (first scores-sorted-with-indices)
      let indices-sorted-by-scores map [pair -> item 1 pair] scores-sorted-with-indices
      let culled-indices sublist indices-sorted-by-scores 0 n-predictors
      set predictors map [index -> item index predictors] culled-indices
  ]]

  tick
end

;; Decide whether to accept advice to change pool
to-report advice-is-credible [recommended-pool predicted-benefit]
  if can-borrow or wealth >= tau [ ;; If we don't have enough wealth to change, or we can't borrow, then the decision is already made for us
    let length-history length filter [choice -> choice = recommended-pool] my-choices
    ifelse length-history > 0 [ ;; do we have any history of trying this choice?
      ;; Calculate average payoff
      let payoff-historical  (reduce + (map [i -> ifelse-value (item i my-choices = recommended-pool)[item i  my-payoffs][0]] range length my-payoffs)) / (length-history)
      report random-float (payoff-historical + tau-weight * tau) < payoff-historical
    ][
      report random-float 1.0 < epsilon  ;; no history, so try with probability epsilon
    ]
  ]
  report False
end

;; Assign colours to pools

to colourize
  let new-color 0
  ask one-of in-link-neighbors [set new-color color]
  set color new-color
end

;; Select a random value in accordance with epcified probabities
;; Use tower sampling - Statistical Mechanics Algorihms and Computations, Wener Krauth
;; http://blancopeck.net/Statistics.pdf
to-report random-tower [probabilities]
  let i 0
  let selector random-float 1
  let threshold item i probabilities
  while [i < length probabilities][
    if selector < threshold [report i]
    set i i + 1
    if i < length probabilities [set threshold threshold + item i probabilities]
  ]
  report i
end

;; Predict count by taking inner weighted sum of previous values
to-report linear-predict-count [counts coefficients]
  let mycounts counts
  while [length mycounts < length coefficients][  ;; If too few values, pad as described by Fogel
    set mycounts fput (random-normal 33 10) mycounts
  ]
  let length-vectors min (list (length mycounts) (length coefficients))
  let inner-product reduce + (map [[a b] -> a * b] sublist mycounts 0 length-vectors sublist coefficients 0 length-vectors)
  report int min (list n-investors abs inner-product)
end

;; This is a generic predictor - use as a model
;; The function controls its behaviour
;;        INIT      Initialize coefficients that make prediction
;;        PREDICT   Predict return for all three pools
;;        CLONE     Copy coefficients and mutate
;;        EVALUATE  Evaluate performace of this set of coefficients
to-report generic-predictor  [function low-payoff high-payoff low-number high-number coefficients]

  if function = ID []

  if function = INIT [  ]

  if function = PREDICT [
    report (list
      RETURN-STABLE-POOL
      ;;...
      ;;...
    )
  ]

  if function = CLONE [   ]
  if function = EVALUATE []
  report NOTHING
end

to-report cartel-predictor  [function low-payoff high-payoff low-number high-number]

  if function = ID [report 2]

  if function = INIT [  ]

  if function = PREDICT [
    report (list 0 0 100 )
  ]

  if function = CLONE [  report (list [[func a b c d] -> cartel-predictor func a b c d ]) ] ;FIXME
  if function = EVALUATE [report 0]
  report NOTHING
end

to-report simple-coarse-grainer2 [element break-even-point]
  report ifelse-value (element < break-even-point) [0][1]
end

to-report simple-coarse-grainer3 [element break-even-point]
  report ifelse-value (element < break-even-point / 1.2)
  [0][
   ifelse-value (element < break-even-point * 1.2) [1][2]]
end

to-report get-matches [low-payoff  high-payoff low-number high-number coarse-grainer]
  let break-low break-even-attendance low-payoff  low-number
  let break-high break-even-attendance high-payoff  high-number
  let target-low (map ([i -> (runresult coarse-grainer item i low-payoff break-low)]) (range n-memory))
  let target-high (map ([i -> (runresult coarse-grainer item i high-payoff break-high)]) (range n-memory))
  report filter [i -> i > 0 and
    (runresult coarse-grainer item i low-payoff break-low) = target-low and
    (runresult coarse-grainer item i high-payoff break-high) = target-high] range length low-payoff
  report []
end

to-report experience-predictor  [function low-payoff high-payoff low-number high-number coarse-grainer]

  if function = ID [report 0]

  if function = INIT [  ]

  if function = PREDICT [
    let indices get-matches  low-payoff  high-payoff low-number high-number coarse-grainer
    ifelse length indices > 0 [
      let payoff-stable  reduce + (map [i -> ifelse-value (item i my-choices = POOL-STABLE)[item i  my-payoffs][0]] range length indices)
      let payoff-low  reduce + (map [i -> ifelse-value (item i my-choices = POOL-LOW)[item i  my-payoffs][0]] range length indices)
      let payoff-high  reduce + (map [i -> ifelse-value (item i my-choices = POOL-HIGH)[item i  my-payoffs][0]] range length indices)
      report (map [v -> ifelse-value (v > 0) [v][epsilon-steady]] (list payoff-stable payoff-low payoff-high))
    ][
      report (list RETURN-STABLE-POOL epsilon-steady epsilon-steady)
    ]

  ]

  if function = CLONE [  report (list [[func a b c d] -> experience-predictor func a b c d coarse-grainer]) ] ;FIXME
  if function = EVALUATE [report 0]
  report NOTHING
end

;; This is the linear predictor
;; The function controls its behaviour
;;        INIT      Initialize coefficients that make prediction
;;        PREDICT   Predict return for all three pools
;;        CLONE     Copy coefficients and mutate
;;        EVALUATE  Evaluate performace of this set of coefficients

to-report linear-predictor [function low-payoff high-payoff low-number high-number coefficients]

  if function = ID [report 1]

  if function = INIT [ ;; Initialize coefficients that make prediction
    let my-coefficients map [r -> -1 + 2 * random-float 1] range (1 + random n-coefficients)
    report  [[func a b c d] -> linear-predictor func a b c d my-coefficients]
  ]

  if function = PREDICT [  ;; Predict return for all three pools
    report (list
      RETURN-STABLE-POOL
      predict-return low-payoff low-number coefficients
      predict-return high-payoff high-number coefficients)
  ]

  if function = CLONE [ ;; Copy coefficients and mutate
    let my-coefficients create-mutate-coefficients coefficients
    report  [[func a b c d] -> linear-predictor func a b c d my-coefficients]
  ]

  if function = EVALUATE [ ;; Evaluate performace of this set of coefficients
    set sum-squares-error 0
    let i 0
    let len length low-number
    while [i < n-history and i < len - 1][
      let historical-low item i low-number
      let historical-high item i high-number
      set i i + 1
      let predicted-low-length linear-predict-count (sublist low-number i len) coefficients
      let predicted-high-length linear-predict-count (sublist high-number i len) coefficients
      let diff-low predicted-low-length - historical-low
      set sum-squares-error sum-squares-error + diff-low * diff-low
      let diff-high predicted-high-length - historical-high
      set sum-squares-error sum-squares-error + diff-high * diff-high
    ]

    report sum-squares-error
  ]

  report NOTHING
end

;; predict return for specific pool
to-report predict-return [payoff number coefficients]
  let estimated-total-return  estimate-return payoff number
  let predicted-length        linear-predict-count number coefficients
  report estimated-total-return / (predicted-length + 1)
end

;; Create new coefficients as described by Fogel and mutate them
to-report  create-mutate-coefficients [coefficients]
  let len new-length coefficients
  ;; If we are reducing length, get rid of last coefficient
  if len < length coefficients [report mutate remove-item len coefficients]

  ;; If increasing, add random coefficient at end
  if len > length coefficients [report mutate lput (-1 + 2 * random-float 1) coefficients]

  report mutate coefficients
end

;; Mutate coefficients as described by Fogel
to-report mutate [coefficients]
  report map [c -> c + random-normal 0 sigma-mutation] coefficients
end

;; Change length of coefficient vector as described by Fogel
;; either increase by one, leave the same, or decrease by one
to-report new-length [coefficients]
  let result -1
  while [result < 1 or result > n-coefficients] [
    let r  random-float 1
    ifelse r < 1.0 / 3.0 [
      set result length coefficients - 1
    ][
      ifelse r < 2.0 / 3.0 [
        report length coefficients
      ][
        set result length coefficients + 1
    ]]]
  report result
end

;; Estimate return from historical data
to-report estimate-return [mypayoffs mynumbers]
;  let weighted-payoffs reduce + (map [[a b]-> a * max (list 1 b)] mypayoffs mynumbers)
  report sub-total-payoff mypayoffs mynumbers / max (list 1 length mypayoffs)
end

to-report break-even-attendance[mypayoffs mynumbers]
  report int ((sub-total-payoff mypayoffs mynumbers) / (length mynumbers))
end

to-report sub-total-payoff [mypayoffs mynumbers]
  report reduce + (map [[a b]-> a * max (list 1 b)] mypayoffs mynumbers)
end

;; Count investors in pool
to-report census [pool-no]
  let mypools pools with [pool-number = pool-no]
  report  ifelse-value (ticks > 0) [sum [first  numbers] of mypools][0]
end

to-report outgoings [pool-no]
  let mypools pools with [pool-number = pool-no]
  let non-zero-payoffs (map [[p n] -> ifelse-value (n > 0)[p][0]] (first [payoffs] of mypools) (first [numbers] of mypools) )
  report  ifelse-value (ticks > 0) [sum non-zero-payoffs / ticks][0];[sum payoffs] of mypools][0]
end

to-report expand-investor [me my-wealth my-payoffs0 my-choices0 my-strategy-index]
  report (map [i -> (list i me my-wealth item i my-payoffs0 item i my-choices0 my-strategy-index tau)] range length my-choices0 )
end

to output-investor-details
  let i-wealth 1
  let i-my-payoffs 2
  let i-my-choices 3
  let i-strategy-index 4
  let my-investors  [(list who wealth my-payoffs my-choices strategy-index)] of investors
  let mapped (map [i -> expand-investor first i (item i-wealth i) (item i-my-payoffs i) (item i-my-choices i) (item i-strategy-index i)] my-investors)
  let flattened (reduce sentence mapped)
  let data-with-headers fput (list "step" "who" "wealth" "payoffs" "choices" "strategy" "tau") flattened
  csv:to-file  user-new-file data-with-headers
end

;; resize
;;
;; Scale wealth for display
;;
to resize
  let richest investors with-max [wealth]
  let max-wealth 0
  ask one-of richest [set max-wealth wealth]
  set size max (list 2 (5 * round wealth / max (list 1 max-wealth)))
end

;; Used to indicate that a reporter has failed to compute a meaningful value
to-report NOTHING
  report -1
end

to-report ID
  report 0
end

;; Used to initialize a predictor
to-report INIT
  report  ID + 1
end

;; Used by a predictor to predict a count
to-report PREDICT
  report  INIT + 1
end

;; Used to clone a predictor
to-report CLONE
  report  PREDICT + 1
end

;; Used to evaluate the parformance of a predictor
to-report EVALUATE
  report  CLONE + 1
end

to-report  POOL-STABLE    ;; Index used for stable pool
  report 0
end

to-report    POOL-LOW      ;; Index used for low risk pool
  report 1
end

to-report    POOL-HIGH     ;; Index used for low risk pool
  report 2
end

;; Return from choosing stable pool

to-report RETURN-STABLE-POOL
  report 1
end

;; Copyright (c) 2018 Simon Crase - see info tab for details of licence
@#$#@#$#@
GRAPHICS-WINDOW
285
10
824
550
-1
-1
12.95122
1
10
1
1
1
0
0
0
1
-20
20
-20
20
0
0
1
ticks
30.0

BUTTON
130
175
194
208
Setup
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
210
175
273
208
Go
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

BUTTON
210
210
273
243
Step
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

SLIDER
3
9
119
42
p-payoff-low
p-payoff-low
0
1
0.5
0.05
1
NIL
HORIZONTAL

SLIDER
130
9
243
42
p-payoff-high
p-payoff-high
0
1
0.25
0.05
1
NIL
HORIZONTAL

SLIDER
3
49
117
82
max-payoff-low
max-payoff-low
0
100
40.0
5
1
NIL
HORIZONTAL

SLIDER
130
49
240
82
max-payoff-high
max-payoff-high
0
100
80.0
5
1
NIL
HORIZONTAL

SLIDER
3
89
103
122
p-start-low
p-start-low
0
1
0.1
.05
1
NIL
HORIZONTAL

SLIDER
130
89
229
122
p-start-high
p-start-high
0
1
0.1
0.05
1
NIL
HORIZONTAL

SLIDER
3
129
98
162
n-investors
n-investors
0
200
100.0
10
1
NIL
HORIZONTAL

SLIDER
130
129
222
162
n-ticks
n-ticks
0
1000
100.0
5
1
NIL
HORIZONTAL

SLIDER
3
169
99
202
tau
tau
0
20
1.0
1
1
NIL
HORIZONTAL

PLOT
1135
350
1335
500
Spread
Wealth
Count
0.0
10.0
0.0
10.0
true
false
"set-plot-pen-mode 1\nset-plot-x-range 0 250\nset-plot-y-range 0 5\nset-histogram-num-bars 20" ""
PENS
"default" 1.0 0 -13345367 true "" "histogram [wealth] of investors"

MONITOR
851
345
954
390
Average Wealth
mean [wealth] of investors
0
1
11

MONITOR
965
345
1051
390
Sigma
standard-deviation [wealth] of investors
1
1
11

SLIDER
3
302
107
335
n-coefficients
n-coefficients
1
25
9.0
1
1
NIL
HORIZONTAL

SLIDER
130
305
222
338
n-predictors
n-predictors
0
25
9.0
1
1
NIL
HORIZONTAL

SLIDER
3
345
95
378
n-history
n-history
2
25
7.0
1
1
NIL
HORIZONTAL

PLOT
837
12
1037
162
Prediction errors
NIL
Sum squared error
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 0 -5825686 true "" "plot mean [sum-squares-error] of investors"

PLOT
838
175
1095
325
Wealth
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"wealth" 1.0 0 -11221820 true "" "plot sum [wealth] of investors"
"payout" 1.0 0 -5825686 true "" "plot sum[total-payoff] of pools"
"Switching" 1.0 0 -955883 true "" "plot (sum[total-payoff] of pools - sum [wealth] of investors )"
"Theoretical" 1.0 0 -7500403 true "" "plot sum[potential-payoff] of pools"

PLOT
1061
13
1284
163
Numbers in each pool
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Stable" 1.0 0 -10899396 true "" "plot census POOL-STABLE"
"Low Risk" 1.0 0 -1184463 true "" "plot census POOL-LOW"
"High Risk" 1.0 0 -2674135 true "" "plot census POOL-HIGH"

SLIDER
5
250
110
283
tau-weight
tau-weight
0.05
2
0.95
0.05
1
NIL
HORIZONTAL

SLIDER
3
380
125
413
sigma-mutation
sigma-mutation
0
5
0.1
0.05
1
NIL
HORIZONTAL

MONITOR
849
414
906
459
Stable
census POOL-STABLE
0
1
11

MONITOR
916
413
976
458
Low Risk
census POOL-LOW
0
1
11

MONITOR
985
415
1048
460
High Risk
census POOL-HIGH
0
1
11

MONITOR
916
462
976
507
Payout
outgoings POOL-LOW
2
1
11

MONITOR
985
464
1039
509
Payout
outgoings POOL-HIGH
2
1
11

PLOT
1125
190
1325
340
Return per step
NIL
NIL
0.0
100.0
0.0
1.0
true
true
"" ""
PENS
"Stable" 1.0 0 -10899396 true "" "plot outgoings POOL-STABLE"
"Low" 1.0 0 -1184463 true "" "plot outgoings POOL-LOW"
"High" 1.0 0 -2674135 true "" "plot outgoings POOL-HIGH"

SWITCH
130
340
250
373
randomize-step
randomize-step
1
1
-1000

SWITCH
3
209
108
242
can-borrow
can-borrow
0
1
-1000

SLIDER
3
420
95
453
epsilon
epsilon
0
1
0.1
0.05
1
NIL
HORIZONTAL

SLIDER
135
380
250
413
p-experiencers
p-experiencers
0
1
0.1
0.05
1
NIL
HORIZONTAL

SLIDER
3
460
97
493
n-memory
n-memory
1
10
1.0
1
1
NIL
HORIZONTAL

SLIDER
135
417
260
450
epsilon-steady
epsilon-steady
0
2
2.0
0.05
1
NIL
HORIZONTAL

BUTTON
130
210
185
243
Details
output-investor-details
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

SWITCH
130
250
250
283
g-random-jump
g-random-jump
1
1
-1000

SLIDER
135
460
227
493
n-cartel
n-cartel
0
25
10.0
5
1
NIL
HORIZONTAL

@#$#@#$#@
## WHAT IS IT?

Testbed to investigate the [Complexity Explorer](https://www.complexityexplorer.org) [Spring Challenge](https://www.complexityexplorer.org/challenges/2-spring-2018-complexity-challenge/submissions)

## HOW IT WORKS

There are twp  breeds of Agent, Investors and Pools. The heart of the model, in `to go`, involves each Investor consulting a predictor, which gives advice on the best Pool for the next step. The investor is responsible for deciding whether or not to accept the advice. Meanwhile the Pools make random decisions whether or not to pay off. Sime predictors use machine learning, so there is a chance for them to tune themselves at the end of each step. Membership of pools is tracked by having each Investor link to the Pool that is it currently in. There are three types of Predictor:

 * a **Linear Predictor** uses a [linear autoregression](https://www.investopedia.com/terms/a/autoregressive.asp) to predict the number of investors in the High and Medium Risk pools during the next step, given the number in the previous few steps;
 * an **Experiencer** compares the present state of the High and Medium Risk pools with the past, checks to see what it did last time this sitiation occurred, and what the outcome was.
 * **Cartel Member**s try to manipulate the numbers in the High Risk Pool, and hence the behaviour of other investors, to benfit themselves.

Those investors who use autoregressive pools are set up with multiple predictors, controlled by the *n-predictors* slider; each predictor is set up with up to *n-coefficients* (random selection). After each step the predictors are tuned:

1. copy each predictor and randomly mutate the coefficients of the clone;
1. evaluate all predictors against historical data to judge thier accuracy;
1. choose the best predictor as the adviser for the next step;
1. cull the predictors by removing the poorest performing 50%.


## HOW TO USE IT

Normal usage is to set the sliders and switches to suitable values, then press _Setup_ followed by _Go_. The View depicts the investors as fishes,  and the pools as faces, which will be happy or sad, depending on whether there was a payout during the current step. Colours are used to indicate to risk of the pool, links indicate the pool to which an investor belongs, and the size of the fish increases with relative wealth.

![Figure missing for View](file:View.jpg)


* **Buttons**
    * **Setup**    Initialize
    * **Step**     Single step for debugging
    * **Go**       Execute model
    * **Details** Dump data from each agent in each step for analysis


 * **Sliders**

    * **n-investors**  Number of investors
    * **n-ticks** Duration of simulation
    * **p-start-low** Probability that an investor will start in low risk pool
    * **p-start-high** Probability that an investor will start in high rish pool
    * **p-payoff-low** Probability that low risk pool will pay off during a tick
    * **p-payoff-high** Probability that low risk pool will pay off during a tick
    * **max-payoff-low** Maximum payoff for low risk pool, to be divided among investors
    * **max-payoff-high** Maximum payoff for high risk pool, to be divided among investors
    * **tau** The cost of switching pools
    * **tau-weight**
    * **n-coefficients** _Maximum_ number of coefficients used by linear predictors (actual numbers chosen at random).
    * **n-predictors** Number of linear predictors
    * **n-history** Number of periods to be used when evaluating predictors
    * **benefit-weight** Amount of weight we give to estimated benefit when comparing with tau
    * **sigma-mutation** Standard deviation when we mutate coefficients
    * **epsilon**
    * **p-experiencers**
    * **n-memory**
    * **epsilon-steady**
    * **n-cartel** Create a cartel who try to manipulate other agents into deserting the High Risk pool. 

 * **Switches**
    * **randomize step** Controls whether model always follows recommendation, or selects a pool at random, with probability determined by estimated benefit.
    * **can-borrow**  Allow wealth to become negative if we need to pay tau to switch
    * **g-random-jump**

 * **Plots**
    * **Spread**
    * **Prediction Errors**
    * **Number in Each Pool**
    * **Wealth**
    * **Return per step**

 * **Monitors**
    * **Average Wealth**
    * **Sigma**
    * **Stable**
    * **Low Risk**
    * **High Risk**
    * **Payout**
    * **Payout**


## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)


    to-report generic-predictor  [function low-payoff high-payoff low-number high-number coefficients]

      if function = ID []

      if function = INIT [  ]

      if function = PREDICT [
        report (list
          RETURN-STABLE-POOL
          ;;...
          ;;...
        )
      ]

      if function = CLONE [   ]
      if function = EVALUATE []
      report NOTHING
    end

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)

[Github repository](https://github.com/weka511/201804)

The machine Learning algorithm was developed by David Fogel et al.   "Inductive reasoning and bounded rationality reconsidered", Fogel, D.B.; Chellapilla, K.; Angeline, P.J., IEEE Transactions on Evolutionary Computation, 1999, v3n2, p142-146.

## COPYRIGHT & LICENCE

MIT License

Copyright (c) 2018 Simon Crase -- simon@greenweaves.nz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

bird side
false
0
Polygon -7500403 true true 0 120 45 90 75 90 105 120 150 120 240 135 285 120 285 135 300 150 240 150 195 165 255 195 210 195 150 210 90 195 60 180 45 135
Circle -16777216 true false 38 98 14

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

fish 2
false
0
Polygon -1 true false 56 133 34 127 12 105 21 126 23 146 16 163 10 194 32 177 55 173
Polygon -7500403 true true 156 229 118 242 67 248 37 248 51 222 49 168
Polygon -7500403 true true 30 60 45 75 60 105 50 136 150 53 89 56
Polygon -7500403 true true 50 132 146 52 241 72 268 119 291 147 271 156 291 164 264 208 211 239 148 231 48 177
Circle -1 true false 237 116 30
Circle -16777216 true false 241 127 12
Polygon -1 true false 159 228 160 294 182 281 206 236
Polygon -7500403 true true 102 189 109 203
Polygon -1 true false 215 182 181 192 171 177 169 164 152 142 154 123 170 119 223 163
Line -16777216 false 240 77 162 71
Line -16777216 false 164 71 98 78
Line -16777216 false 96 79 62 105
Line -16777216 false 50 179 88 217
Line -16777216 false 88 217 149 230

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

shark
false
0
Polygon -7500403 true true 283 153 288 149 271 146 301 145 300 138 247 119 190 107 104 117 54 133 39 134 10 99 9 112 19 142 9 175 10 185 40 158 69 154 64 164 80 161 86 156 132 160 209 164
Polygon -7500403 true true 199 161 152 166 137 164 169 154
Polygon -7500403 true true 188 108 172 83 160 74 156 76 159 97 153 112
Circle -16777216 true false 256 129 12
Line -16777216 false 222 134 222 150
Line -16777216 false 217 134 217 150
Line -16777216 false 212 134 212 150
Polygon -7500403 true true 78 125 62 118 63 130
Polygon -7500403 true true 121 157 105 161 101 156 106 152

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.0.3
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="experiment" repetitions="25" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="100"/>
    <metric>census POOL-STABLE</metric>
    <metric>outgoings POOL-STABLE</metric>
    <metric>census POOL-LOW</metric>
    <metric>outgoings POOL-LOW</metric>
    <metric>census POOL-HIGH</metric>
    <metric>outgoings POOL-HIGH</metric>
    <metric>mean [wealth] of investors</metric>
    <metric>standard-deviation [wealth] of investors</metric>
    <metric>mean [sum-squares-error] of investors</metric>
    <enumeratedValueSet variable="max-payoff-high">
      <value value="80"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-ticks">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-start-low">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-history">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-investors">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-start-high">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-payoff-low">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-payoff-high">
      <value value="0.25"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="sigma-mutation">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="randomize-step">
      <value value="true"/>
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="can-borrow">
      <value value="true"/>
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="tau">
      <value value="0"/>
      <value value="1"/>
      <value value="5"/>
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-predictors">
      <value value="3"/>
      <value value="6"/>
      <value value="9"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-payoff-low">
      <value value="40"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-coefficients">
      <value value="3"/>
      <value value="6"/>
      <value value="9"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="many-agents" repetitions="12" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="100"/>
    <metric>census POOL-STABLE</metric>
    <metric>outgoings POOL-STABLE</metric>
    <metric>census POOL-LOW</metric>
    <metric>outgoings POOL-LOW</metric>
    <metric>census POOL-HIGH</metric>
    <metric>outgoings POOL-HIGH</metric>
    <metric>mean [wealth] of investors</metric>
    <metric>standard-deviation [wealth] of investors</metric>
    <metric>mean [sum-squares-error] of investors</metric>
    <enumeratedValueSet variable="max-payoff-high">
      <value value="80"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-ticks">
      <value value="1000"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-start-low">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-history">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="benefit-weight">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-investors">
      <value value="100"/>
      <value value="200"/>
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-start-high">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-payoff-low">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-payoff-high">
      <value value="0.25"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="sigma-mutation">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="randomize-step">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="can-borrow">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="tau">
      <value value="0"/>
      <value value="1"/>
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-predictors">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-payoff-low">
      <value value="40"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-coefficients">
      <value value="6"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="experiment" repetitions="1" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <metric>all-investors</metric>
    <enumeratedValueSet variable="max-payoff-high">
      <value value="80"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-ticks">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="can-borrow">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-start-low">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-experiencers">
      <value value="0.15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-history">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="tau-weight">
      <value value="0.65"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="epsilon2">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-investors">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-start-high">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-payoff-low">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-memory">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-payoff-high">
      <value value="0.25"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="sigma-mutation">
      <value value="0.15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="randomize-step">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="tau">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-predictors">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="epsilon">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-payoff-low">
      <value value="40"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-coefficients">
      <value value="6"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="cartel" repetitions="25" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <metric>outgoings POOL-HIGH</metric>
    <enumeratedValueSet variable="max-payoff-high">
      <value value="80"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-ticks">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="can-borrow">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-start-low">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-experiencers">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-history">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="g-random-jump">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="tau-weight">
      <value value="0.95"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-investors">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-cartel">
      <value value="0"/>
      <value value="1"/>
      <value value="2"/>
      <value value="5"/>
      <value value="10"/>
      <value value="15"/>
      <value value="20"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-start-high">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-memory">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-payoff-low">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="sigma-mutation">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-payoff-high">
      <value value="0.25"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="randomize-step">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="tau">
      <value value="0"/>
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-predictors">
      <value value="9"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="epsilon">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-payoff-low">
      <value value="40"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="epsilon-steady">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="n-coefficients">
      <value value="9"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
1
@#$#@#$#@
