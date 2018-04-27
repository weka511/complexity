extensions[CSV]

patches-own [
  pool-number  ;; Used to translate from colour to numbers used in Tournament
]

turtles-own [
  wealth        ;; accumulated payout, allowing for tau
  favourite
  my-predictors ;; these tell me what course to follow
  payoffs       ;; list of payouts, most recent first, before tau subtracted
  choices       ;; list of choices made by turtle, most recent first
]


globals [
  g-low-payoff  ;; list of  payouts per agent from low pool, most recent first
  g-high-payoff ;; list of  payouts per agent from high pool, most recent first
  g-low-number  ;; list of numbers of agents in low pool, most recent first
  g-high-number ;; list of numbers of agents in high pool, most recent first
  g-predictor-pool
]

;; Set up patches and investors

to setup
  clear-all

  ;; Initialize globals

  set g-low-payoff []
  set g-high-payoff []
  set g-low-number []
  set g-high-number []
  set g-predictor-pool []
  foreach csv:from-file "predictors.csv" [
    [row] -> repeat item 1 row [
      set g-predictor-pool lput row g-predictor-pool
  ]]

  ask patches[
    establish-pools
  ]

  create-turtles n-agents [
    establish-turtle
  ]

  reset-ticks
end


;; Collect any payout and decide whether to change pools

to go
  if ticks >= n-steps [stop]

  let payoff_low_risk get-payoff yellow
  let pay-dividend-low? pay-dividend? [yellow]
  let payoff_high_risk get-payoff red
  let pay-dividend-high? pay-dividend? [red]

  ask turtles [
    ;; Calculate payout for this step
    let my-payoff 1   ;; assume stable
    if pcolor = red [
      set my-payoff ifelse-value pay-dividend-high? [payoff_high_risk] [0]
    ]
    if pcolor = yellow [
      set my-payoff ifelse-value pay-dividend-low? [payoff_low_risk] [0]
    ]

    set wealth wealth + my-payoff

    ;; Decide whether to switch pools

    ifelse length choices =  0 [
      set choices lput pool-number choices
    ][
      let new-pool choose-strategy g-low-payoff g-high-payoff g-low-number g-high-number payoffs choices

      ifelse new-pool = pool-number [
        display-wealth
      ][
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
      set choices lput new-pool choices
    ]
   set payoffs lput my-payoff payoffs
  ]

  ;; Update history

  set g-low-payoff lput payoff_low_risk  g-low-payoff
  set g-high-payoff lput payoff_high_risk  g-high-payoff
  let n-payees-low count turtles with [pcolor = yellow]
  set g-low-number lput n-payees-low  g-low-number
  let n-payees-high count turtles with [pcolor = red]
  set g-high-number lput n-payees-high g-high-number

  tick
end

;; Set up an investor

to establish-turtle
  set payoffs []
  set choices []
  set my-predictors n-of n-predictors g-predictor-pool
  set favourite one-of my-predictors
  set shape "sheep"
  set size 2
  set color white
  set wealth 0
  display-investor choose-initial-pool
end




to-report choose-initial-pool
    let p2 p-low0 + p-high0
    let p random-float 1
    let pool 0
    ifelse p < p-low0[
      set pool 1
    ][
      if p < p2[
        set pool 2
    ]]
  report pool
end

to display-investor [pool]
  ifelse pool = 0 [
    set xcor 2 * min-pxcor / 3
  ][
    ifelse pool = 1 [
      set xcor 0
  ][ set xcor 2 * max-pxcor / 3]]
  let offset ( min-pxcor + 2 * max-pxcor * random-float 1.0) / 4
  set xcor xcor + offset
  display-wealth
end

to display-wealth
   set ycor min (list (max-pycor - 2)  (wealth + min-pycor + 2))
end

;; Convert a patch colour to a pool number

to-report colour2pool
  if pcolor = red[report 2]
  if pcolor = yellow[report 1]
  report 0
end

;; Assign background colours and pool numbers to patches

to establish-pools
    set pcolor yellow
    if pxcor > max-pxcor / 3 [set pcolor red]
    if pxcor < min-pxcor / 3 [set pcolor green]
    set pool-number colour2pool
end

;; Decide whether or not a pool will payoff this tick
;; High pays one in 4 ticks, low one in 2
to-report pay-dividend? [pool-colour]
  let odds ifelse-value (pool-colour = red) [4][2]
  report random odds = 0
end

;; Compute payoff for specified pool, assuming it occurs
;; i.e. dividend per eligible investor

to-report get-payoff [pool-colour]
  let dividend ifelse-value (pool-colour = red) [80][40]
  let n-payees count turtles with [pcolor = pool-colour]
  report dividend / max list n-payees 1
end

to-report stay [my-payoffs my-choices]
  report item 0 my-choices
end

to-report random-jump [my-payoffs my-choices]
  report (random 2)
end

to-report use-number [my-payoffs my-choices action-list]
  let estimator get-estimator action-list
  let estimate-low-number (runresult estimator g-low-number action-list)
  let estimate-low-payoff (80 / 4) / (estimate-low-number + 1)
  let estimate-high-number (runresult estimator g-high-number action-list)
  let estimate-high-payoff (20 / 2) / (estimate-high-number + 1)
  let pool 0
  let predicted-payoff 1
  if estimate-low-payoff > predicted-payoff [
    set pool 1
    set predicted-payoff estimate-low-payoff
  ]
  if estimate-high-payoff > predicted-payoff [
    set pool 2
    set predicted-payoff estimate-high-payoff
  ]
  report pool
end

to-report get-estimator [action-list]
  let estimator-name item 2 action-list

  if estimator-name = "Average" [
    report [ [a] -> get-average a action-list]
  ]
end

to-report get-average [pool action-list]
  let i 0
  let j 3
  let total 0
  let total-weight 0
  while [i < length pool and j < length action-list] [
    let weight item j action-list
    set total total + weight * item i pool
    set total-weight total-weight + weight
    set i i + 1
    set j j + 1
  ]
  report ifelse-value ( total-weight > 0 ) [total / total-weight] [0]
end

to-report get-action [action-list]
  let action-name item 0 action-list

  if action-name = "Stay" [
    report [[a b] -> stay a b]
  ]

  if action-name = "Random" [
    report [[a b] -> random-jump a b]
  ]

  if action-name = "Number" [
    report [[a b] -> use-number a b action-list]
  ]

end

to-report choose-strategy [
  low-payoff  ;; list of  payouts per agent from low pool, most recent first
  high-payoff ;; list of  payouts per agent from high pool, most recent first
  low-number  ;; list of numbers of agents in low pool, most recent first
  high-number ;; list of numbers of agents in high pool, most recent first
  my-payoffs  ;; list of payouts, most recent first, before tau subtracted
  my-choices]  ;; list of choices made by turtle, most recent first
let action get-action favourite
report (runresult action low-payoff high-payoff low-number my-choices my-choices my-payoffs)

end
@#$#@#$#@
GRAPHICS-WINDOW
210
10
647
448
-1
-1
13.0
1
10
1
1
1
0
0
0
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
0
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
0
200
101.0
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
10
135
102
168
p-low0
p-low0
0
1
0.33
0.01
1
NIL
HORIZONTAL

SLIDER
108
135
200
168
p-high0
p-high0
0
1
0.33
0.01
1
NIL
HORIZONTAL

PLOT
10
175
210
312
Counts
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
"default" 1.0 0 -10899396 true "" "plot count turtles with [pcolor = green]"
"pen-1" 1.0 0 -1184463 true "" "plot count turtles with [pcolor = yellow]"
"pen-2" 1.0 0 -2674135 true "" "plot count turtles with [pcolor = red]"

PLOT
11
316
211
451
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
"Stable" 1.0 0 -10899396 true "" "plot mean [wealth] of turtles with [pcolor = green]"
"Low" 1.0 0 -1184463 true "" "plot mean [wealth] of turtles with [pcolor = yellow]"
"pen-2" 1.0 0 -2674135 true "" "plot mean [wealth] of turtles with [pcolor = red]"

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
25
460
197
493
n-predictors
n-predictors
1
10
5.0
1
1
NIL
HORIZONTAL

@#$#@#$#@
## WHAT IS IT?

Testbed to investigate the [Complexity Explorer](https://www.complexityexplorer.org) [Spring Challenge](https://www.complexityexplorer.org/challenges/2-spring-2018-complexity-challenge/submissions)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

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
