# Complexity Explorer Challenge 2018 April

## Problem Statement

[Read at Complexity Explorer](https://www.complexityexplorer.org/challenges/2-spring-2018-complexity-challenge/submissions)

  
## Files

| Name | Purpose |
|--------------------|--------------------------------------------------------------------------|
| 201804.bib | Bibtex input to documentation |
| 201804.xml | Workspace for Notepad++ | 
| challenge.Rmd | Writeup for submission to SFI |
| get-data.r | Script to initialize data for challenge.Rmd |
|~~ieee.csl| Required by challenge.Rmd to build bibliography~~ |
| ieee-with-url |Required by challenge.Rmd to build bibliography |
| Proposal.pdf | Agent Based Modelling Proposal |
| Proposal.tex | Agent Based Modelling Proposal |
| README.md | This File |
| sheep-wall-street.nlogo | Original Testbed for evaluating alternative strategies |
| take2.nlogo | New model using links for assignment to pool |
| strategies.csv | Parameters for strategies |
| View.jpg | Image for Infor tab of take2.nlogo |
| ~~Writeup.pdf | Writeup for submission to SFI (obsolete)~~ |
| ~~Writeup.tex | Writeup for submission to SFI (obsolete) ~~|

## Journal

| Date | Remarks |
|-----------|--------------------------------------------------------------------------------|
|24&nbsp;Apr&nbsp;2018| Started. Created repository and Wrote up Proposal |
| 27 Apr 2018 |Started implementing focal rules as in the original El Farol paper. Also started reading the Kolkaka Paise restaurant papers. Think about criteria for evaluating rules, e.g. review every n iterations to see whther I could do better, review against target performance, etc.|
| 8 May 2018 | Started on machine Learning after Fogel. I need to think through starting conditions. Is there enough time to start the way Fogel does? |
| 9 May 2018 | Started new version of model, using links for assignments to pools. Size of Fish (investors) indicates wealth, and happ/sad face indicates whether pool has paid off.|
| 10&nbsp;May&nbsp;2018| Performed experiments on function closure. Bindings captured as doco indicates. Also function can recurse. So will use a function for predictor, withone argument indicating whther we want to initialize, predict or train.|
| 11 May 2018 | Learning is converging to same estimates |
| 13 May 2018 | I've digressed into working out how to use RMarkdown for writing up the challenge|



