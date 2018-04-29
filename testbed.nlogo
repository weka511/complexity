extensions[
  CSV
]

patches-own [
  pool-number  ;; Used to translate from colour to numbers used in Tournament
]

turtles-own [
  wealth               ;; accumulated payout, allowing for tau
  favourite-predictor  ;; the predictor that is actually used to switch pools
  predictor-index      ;; index of favourite-predictor in candidates
  candidate-predictors ;; a pool of predictors, which could be used if
                       ;; favourite-predictor is not performing well
  payoffs              ;; list of payouts, most recent first, before tau subtracted
  choices              ;; list of choices made by turtle, most recent first
  alternative-choices  ;; the choices that the alternative-payoffs would have recommended
                       ;; during the last n-review time steps
  alternative-payoffs  ;; the payoffs if the alternative-choices had been made
]

globals [
  g-low-payoff                 ;; list of  payouts per agent from low pool, most recent first
  g-high-payoff                ;; list of  payouts per agent from high pool, most recent first
  g-low-number                 ;; list of numbers of agents in low pool, most recent first
  g-high-number                ;; list of numbers of agents in high pool, most recent first
  g-changed-predictors         ;; Number of predictors that were replaced in the current round
  g-ticks-without-change       ;; Number of ticks that have had no change in predictors
                               ;; Reset each time even one predictor changed
  g-changed-assignments        ;; Number of pools chnaged during current round
  g-maximum-wealth-for-scaling ;; Maximum wealth this round - used to scale output area
]

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Define constants

to-report  POOL-STABLE    ;; Index used for stable pool
  report 0
end

to-report    POOL-LOW      ;; Index used for low risk pool
  report 1
end

to-report    POOL-HIGH     ;; Index used for low risk pool
  report 2
end

to-report   ZILCH   ;; Payoff of 0
  report 0
end

to-report   PRED-ACTION    ;; index of action in predictor row
  report 0
end

to-report    PRED-COUNT    ;; index of count in predictor row
  report 1
end

to-report   PRED-ESTIMATOR ;; index of action in predictor row
  report 2
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Top level procedures

;; Set up patches and investors

to setup
  clear-all

  ;; Initialize globals

  set g-low-payoff  []
  set g-high-payoff []
  set g-low-number  []
  set g-high-number []

  set g-changed-predictors   0
  set g-ticks-without-change 0
  set g-changed-assignments  0
  set g-maximum-wealth-for-scaling n-steps * payoff-stable

  ask patches[
    establish-pools
  ]

  ;; Create big pool of all predictors;
  ;; each turtle gets a subset
  let predictor-pool []
  foreach csv:from-file "predictors.csv" [
    [row] -> repeat item PRED-COUNT row [
      set predictor-pool fput row predictor-pool
  ]]

  create-turtles n-agents [
    establish-turtle  predictor-pool
  ]

  reset-ticks
end

;; Calculate payout from favourite proeictor and alternatives and
;; update history. Decode whther to change pool or predictor.
to go
  if ticks >= n-steps [
    save-rules
    stop
  ]

  let payoff_low_risk get-payoff yellow
  let pay-dividend-low? pay-dividend? [yellow]
  let payoff_high_risk get-payoff red
  let pay-dividend-high? pay-dividend? [red]

  set g-changed-assignments 0
  ask turtles [
    calculate-payout-for-this-step payoff_low_risk pay-dividend-low? payoff_high_risk pay-dividend-high?
    determine-alternative-choices
  ]

  ;; Update history

  set g-low-payoff fput ifelse-value pay-dividend-low? [payoff_low_risk] [0] g-low-payoff
  set g-high-payoff fput ifelse-value pay-dividend-high? [payoff_high_risk] [0]  g-high-payoff
  let n-payees-low count turtles with [pcolor = yellow]
  set g-low-number fput n-payees-low  g-low-number
  let n-payees-high count turtles with [pcolor = red]
  set g-high-number fput n-payees-high g-high-number

  ask turtles [
    determine-alternative-payoffs
  ]

  set g-changed-predictors 0
  if ticks mod n-review = 0 and ticks > n-horizon[
    ask turtles[
      review-predictors
    ]
  ]
  set g-ticks-without-change ifelse-value (g-changed-predictors = 0) [g-ticks-without-change + 1][0]
  set g-maximum-wealth-for-scaling 1
  ask turtles [
    set g-maximum-wealth-for-scaling max (list g-maximum-wealth-for-scaling wealth)
  ]
  tick
end



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; implementation

;; Collect any payout and decide whether to change pools

to calculate-payout-for-this-step [payoff_low_risk pay-dividend-low? payoff_high_risk pay-dividend-high?]
  let my-payoff get-payout-for-this-step payoff_low_risk pay-dividend-low? payoff_high_risk pay-dividend-high?
  set wealth wealth + my-payoff
  decide-whether-to-switch-pools
  set payoffs fput my-payoff payoffs
end

;; Calculate actual payout for specific turtle
to-report get-payout-for-this-step [payoff_low_risk pay-dividend-low? payoff_high_risk pay-dividend-high?]
  if pcolor = red [report ifelse-value pay-dividend-high? [payoff_high_risk] [ZILCH] ]
  if pcolor = yellow [report ifelse-value pay-dividend-low? [payoff_low_risk] [ZILCH] ]
  report payoff-stable
end

;; Decide whether to switch pools
to decide-whether-to-switch-pools
     ifelse length choices =  0 [
      set choices fput pool-number choices
    ][
      let new-pool (runresult (get-action favourite-predictor) payoffs choices)

      ifelse new-pool = pool-number [
        display-wealth
      ][
      set g-changed-assignments g-changed-assignments + 1
        ifelse wealth >= tau [
          set wealth wealth - tau
          display-investor new-pool
        ][
          if can-borrow = "yes"[
            set wealth wealth - tau
            display-investor new-pool
          ]
          if can-borrow = "no"[display-wealth]
          if can-borrow = "die"[die]
        ]
      ]
      set choices fput new-pool choices
    ]
end

;; Find out what each of the alternative prodictrs would have done
;; so we can cualate altenative payouts
to determine-alternative-choices
  if length choices >  1 [  ;; TODO - why does program crash without this?
    let alternatives-for-this-step map [predictor -> (runresult (get-action predictor) payoffs choices)] candidate-predictors
    set alternative-choices lput alternatives-for-this-step  alternative-choices
    if length alternative-choices > n-review [set alternative-choices remove-item 0 alternative-choices]
  ]
end

;; Calculate what payouts would have been with different prodictors.
;; TODO: allow for tau
to determine-alternative-payoffs
  if length alternative-choices > 0 [
    let alternatives item (length alternative-choices - 1) alternative-choices
    let actual-choice item 0 choices
    let alt-n-payees-low map [alt-choice -> adjust-numbers (alt-choice = POOL-LOW) (item 0 g-low-number) (actual-choice = POOL-LOW)] alternatives
    let alt-n-payees-high map [alt-choice -> adjust-numbers (alt-choice = POOL-HIGH) (item 0 g-high-number) (actual-choice = POOL-HIGH)] alternatives
    let alternative-payout map [i -> get-alternative-payout (item i alternatives) (item i alt-n-payees-low) (item i alt-n-payees-high)] (n-values n-horizon [ j -> j ])
    set alternative-payoffs lput alternative-payout alternative-payoffs
  ]
end

;; Calculate what payouts would have been with specific choice.
;; TODO: allow for tau
to-report  get-alternative-payout [choice n-low n-high]
  report ifelse-value (choice = POOL-STABLE) [payoff-stable][
    ifelse-value (choice = POOL-LOW) [
      payoff-risk-pool n-low (item 0 g-low-number) (item 0 g-low-payoff)
    ][
     payoff-risk-pool n-high (item 0 g-high-number) (item 0 g-high-payoff)
    ]]
end

;; Calculate payout from high or low risk pool
to-report payoff-risk-pool [n-alternative n-actual actual-total-payoff]
  report ifelse-value (actual-total-payoff = 0) [0] [actual-total-payoff * (max (list 1 n-actual))  / max (list 1 n-alternative)]
end

;; Recalculate numbers in low or high point, after replacing choice with alternative
to-report adjust-numbers [alt-choice number choice]
  report number + ifelse-value alt-choice [1][0] - ifelse-value choice [1][0]
end


;; Set up an investor with a collection of predictors
;; and assign to a pool

to establish-turtle  [predictor-pool]
  set payoffs []
  set choices []
  set candidate-predictors n-of n-predictors predictor-pool
  set predictor-index random length candidate-predictors
  set favourite-predictor item predictor-index  candidate-predictors
  let shape-index  predictor-index mod length shapes
  set shape item shape-index  shapes
  set size 1
  set color white
  set wealth starting-wealth
  set alternative-payoffs []
  set alternative-choices []

  display-investor choose-initial-pool
end

;; Decide how much wealth each individual starts with

to-report starting-wealth  ;; TODO - allow flexibility
  report 0
end

;; Allocate agents to pools at the start

to-report choose-initial-pool
  let rvalue random-float 1

  if rvalue < p-low0 [report POOL-LOW]
  if rvalue < (p-low0 + p-high0) [report POOL-HIGH]
  report POOL-STABLE
end

to-report get-x [pool]
  if pool = POOL-STABLE [report 2 * min-pxcor / 3]
  if pool = POOL-LOW [report 0]
  report  2 * max-pxcor / 3 ;; POOL-HIGH
end

to display-investor [pool]
  set xcor get-x pool + ( min-pxcor + 2 * max-pxcor * random-float 1.0) / 4
  display-wealth
end

to display-wealth
   set ycor min-pycor +  ((max-pycor - min-pycor) * wealth / g-maximum-wealth-for-scaling)
end

;; Convert a patch colour to a pool number

to-report colour2pool
  if pcolor = red [report POOL-HIGH]
  if pcolor = yellow [report POOL-LOW]
  report POOL-STABLE
end

;; Assign background colours and pool numbers to patches

to establish-pools
    set pcolor yellow
    if pxcor > max-pxcor / 3 [set pcolor red]
    if pxcor < min-pxcor / 3 [set pcolor green]
    set pool-number colour2pool
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Predictors and choice of strategy

to-report accumulate [a b]
  let result   []
  let i 0
  while [i < length a] [
    set result fput (item i a + item i b) result
    set i i + 1
  ]
  report result
end

to review-predictors
  ifelse evaluate-altenatives? [
    let scores   n-values n-horizon [i -> 0]
    let i 0
    while [i < length alternative-payoffs] [
      set scores accumulate item i alternative-payoffs scores
      set i i + 1
    ]

    let max-score max scores
    if max-score > n-grace + item predictor-index scores [
      set g-changed-predictors g-changed-predictors + 1
      let full-indices n-values (length scores) [ j -> j ]
      let max-indices filter [j -> item j scores = max-score] full-indices
      set predictor-index  one-of max-indices
      set favourite-predictor item predictor-index  candidate-predictors
      let shape-index  predictor-index mod length shapes
      set shape item shape-index  shapes
    ]
  ][
    let best-payoff max (
      list
      (payoff-stable * n-horizon)
      truncate-history-horizon g-low-payoff
      truncate-history-horizon g-low-payoff)
    let my-payout truncate-history-horizon payoffs
    if my-payout + n-grace < best-payoff [
      set g-changed-predictors g-changed-predictors + 1
      let new-predictor-index predictor-index
      while [new-predictor-index = predictor-index] [
        set new-predictor-index random length candidate-predictors
      ]
      set predictor-index  new-predictor-index
      set favourite-predictor item predictor-index  candidate-predictors
      let shape-index  predictor-index mod length shapes
      set shape item shape-index  shapes
    ]

  ]
end

to-report truncate-history-horizon [history]
  report sum n-values n-horizon [ i -> item i history]
end

to-report score-predictor [predictor]  ;; TODO
  report sum(map [i -> score-one i predictor ] n-values n-horizon [ i -> i ])
end

to-report score-one [index predictor]  ;; TODO
  let predicted-pool (runresult (get-action predictor) payoffs choices)
  report 0
end

to save-rules
  let rules []
  ask turtles[
    set rules lput favourite-predictor rules
  ]
  csv:to-file "out.csv" rules
end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Actions

;; Find the action that has been stepicified
to-report get-action [action-list]
  let action-name item PRED-ACTION action-list
  if action-name = "Stay" [report [[a b] -> stay a b]]
  if action-name = "Random" [report [[a b] -> random-jump a b]]
  if action-name = "Number" [report [[a b] -> use-number a b action-list] ]
end

to-report stay [my-payoffs my-choices]
  report item 0 my-choices
end

to-report random-jump [my-payoffs my-choices]
  report (random 2)
end

;; Decide which pool to join by predicting the number of investors in each
;; pool, predicting expected payoff, then choosing the pool that maximizes
;; the expected payoff
to-report use-number [dummy1 dummy2 action-list]
  let estimator get-estimator action-list
  let estimate-low-number (runresult estimator g-low-number action-list)
  let estimate-low-payoff (max-low-payoff * p-low-payoff) / (estimate-low-number + 1)
  let estimate-high-number (runresult estimator g-high-number action-list)
  let estimate-high-payoff (max-high-payoff * p-high-payoff) / (estimate-high-number + 1)

  let pool POOL-STABLE   ; Assume stable pool - see if other two can do better
  let predicted-payoff payoff-stable
  if estimate-low-payoff > predicted-payoff [
    set pool POOL-LOW
    set predicted-payoff estimate-low-payoff
  ]
  if estimate-high-payoff > predicted-payoff [set pool POOL-HIGH]
  report pool
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Estimators

to-report get-estimator [action-list]
  let estimator-name item PRED-ESTIMATOR  action-list
  if estimator-name = "Cycle" [report [ [a] -> get-cycle a action-list]]
  if estimator-name = "Average" [report [ [a] -> get-average a action-list]]
  if estimator-name = "Trend" [report [ [a] -> get-trend a action-list]]
end

;; Look for cycles
to-report get-cycle [history action-list]
  let n item (PRED-ESTIMATOR + 1) action-list
  report ifelse-value (n < length history) [item n history] [item 0 history]
end

;; Calculate weighted average of history (numbers in low wisk or high risk pool)
to-report get-average [history action-list]
  let i 0
  let j PRED-ESTIMATOR + 1
  let weighted-sum 0
  let total-weight 0
  while [i < length history and j < length action-list] [
    let weight item j action-list
    set weighted-sum weighted-sum + weight * item i history
    set total-weight total-weight + weight
    set i i + 1
    set j j + 1
  ]
  report ifelse-value ( total-weight > 0 ) [weighted-sum / total-weight] [0]
end

;l Use trend to estimate number
;;
;; Formulae snarfed from
;; http://www.statisticshowto.com/probability-and-statistics/regression-analysis/find-a-linear-regression-equation/

to-report get-trend [history action-list]
  if length history < 2 [report item 0 history]
  let n min (list length history item (PRED-ESTIMATOR + 1) action-list)
  let n-min item (PRED-ESTIMATOR + 2) action-list
  let n-max item (PRED-ESTIMATOR + 3) action-list
  let xs n-values n [ i -> i ]
  let ys n-values n [ i -> item i history]
  let sum_y sum(ys)
  let sum_xsq sum(map [x -> x * x] xs)
  let sum_x sum (xs)
  let sum_xy  sum (map [i -> i * (item i ys)] xs)
  let a (sum_y * sum_xsq - sum_x * sum_xy )/(n * sum_xsq - sum_x * sum_x)
  let b (n * sum_xy - sum_x * sum_y )/(n * sum_xsq - sum_x * sum_x)
  let raw-prediction round(a - b) ; a + (-1) * b
  report ifelse-value (raw-prediction  < n-min) [n-min] [ifelse-value (raw-prediction  < n-max)[raw-prediction ][n-max]]
end




;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; payoffs

;; Decide whether or not a pool will payoff this tick
;; High pays one in 4 ticks, low one in 2
to-report pay-dividend? [pool-colour]
  let probability ifelse-value (pool-colour = red) [p-high-payoff][p-low-payoff]
  report (random-float 1) < probability
end

;; Compute payoff for specified pool, assuming it occurs
;; i.e. dividend per eligible investor

to-report get-payoff [pool-colour]
  let dividend ifelse-value (pool-colour = red) [max-high-payoff][max-low-payoff]
  let n-payees count turtles with [pcolor = pool-colour]
  report dividend / max list n-payees 1
end

;; Copyright (c) 2018 Simon Crase - see info tab for details of licence
@#$#@#$#@
GRAPHICS-WINDOW
845
10
1259
425
-1
-1
12.303030303030303
1
10
1
1
1
0
1
1
1
-16
16
-16
16
0
0
1
ticks
30.0

BUTTON
10
10
65
43
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
141
10
196
45
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
78
10
133
43
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
10
48
102
81
n-agents
n-agents
3
100
50.0
1
1
NIL
HORIZONTAL

SLIDER
110
50
202
83
n-steps
n-steps
1
1000
100.0
1
1
NIL
HORIZONTAL

SLIDER
10
85
102
118
tau
tau
1
100
10.0
1
1
NIL
HORIZONTAL

SLIDER
220
90
312
123
p-low0
p-low0
0
1
0.1
0.01
1
NIL
HORIZONTAL

SLIDER
318
90
410
123
p-high0
p-high0
0
1
0.1
0.01
1
NIL
HORIZONTAL

PLOT
5
130
420
267
Counts
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
"Stable" 1.0 0 -10899396 true "" "plot count turtles with [pcolor = green]"
"Low Risk" 1.0 0 -1184463 true "" "plot count turtles with [pcolor = yellow]"
"High Risk" 1.0 0 -2674135 true "" "plot count turtles with [pcolor = red]"

PLOT
220
270
420
405
Wealth
NIL
NIL
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"Stable" 1.0 0 -10899396 true "" "plot sum [wealth] of turtles with [pcolor = green]"
"Low" 1.0 0 -1184463 true "" "plot sum [wealth] of turtles with [pcolor = yellow]"
"High" 1.0 0 -2674135 true "" "plot sum [wealth] of turtles with [pcolor = red]"

CHOOSER
110
85
202
130
can-borrow
can-borrow
"yes" "no" "die"
1

SLIDER
605
10
697
43
n-predictors
n-predictors
1
20
10.0
1
1
NIL
HORIZONTAL

SLIDER
710
10
802
43
n-review
n-review
1
n-steps
5.0
1
1
NIL
HORIZONTAL

SLIDER
225
10
335
43
max-low-payoff
max-low-payoff
1
100
40.0
1
1
NIL
HORIZONTAL

SLIDER
350
10
475
43
max-high-payoff
max-high-payoff
1
100
80.0
1
1
NIL
HORIZONTAL

SLIDER
225
50
345
83
p-low-payoff
p-low-payoff
0
1
0.5
0.01
1
NIL
HORIZONTAL

SLIDER
350
50
475
83
p-high-payoff
p-high-payoff
0
1
0.25
0.01
1
NIL
HORIZONTAL

SLIDER
710
50
802
83
n-horizon
n-horizon
1
n-steps
10.0
1
1
NIL
HORIZONTAL

SLIDER
605
50
700
83
n-grace
n-grace
0
n-steps
100.0
1
1
NIL
HORIZONTAL

SLIDER
490
10
600
43
payoff-stable
payoff-stable
0
100
1.0
1
1
NIL
HORIZONTAL

SWITCH
595
90
755
123
evaluate-altenatives?
evaluate-altenatives?
0
1
-1000

PLOT
425
145
825
295
Changes to predictors
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
"Changes" 1.0 0 -11221820 true "" "plot g-changed-predictors"
"Unchanged" 1.0 0 -5825686 true "" "plot g-ticks-without-change"
"Pool changes" 1.0 0 -955883 true "" "plot g-changed-assignments"

PLOT
5
270
205
420
Average Wealth
NIL
NIL
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 0 -10899396 true "" "plot (sum [wealth] of turtles with [pcolor = green]) / max (list count turtles with [pcolor = green] 1)"
"pen-1" 1.0 0 -1184463 true "" "plot (sum [wealth] of turtles with [pcolor = yellow]) / max (list count turtles with [pcolor = yellow] 1)"
"pen-2" 1.0 0 -2674135 true "" "plot (sum [wealth] of turtles with [pcolor = red]) / max (list count turtles with [pcolor = red] 1)"

@#$#@#$#@
## WHAT IS IT?

Testbed to investigate the [Complexity Explorer](https://www.complexityexplorer.org) [Spring Challenge](https://www.complexityexplorer.org/challenges/2-spring-2018-complexity-challenge/submissions)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

 * Buttons
    * Setup
    * Step
    * Go
  * n-agents
  * n-steps
  * tau
  * can-borrow
  * p-low0
  * p-high0
  * Counts
  * Wealth
  * n-predictors
  * Review
    * n-review
    * n-horizon
    * n-grace
  * Pools
    * max-low-payoff
    * max-high-payoff
    * freq-low-payoff
    * freq-high-payoff

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)

[Github repository](https://github.com/weka511/201804)

## COPYRIGHT & LICENCE

MIT License

Copyright (c) 2018 Simon Crase

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
