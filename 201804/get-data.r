# MIT License
# 
# Copyright (c) 2018 Simon Crase
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

rm(list=ls())

library(plyr)

# fix.column.names
#
# Remove dots from column names, as they confuse R: foo$bar_baz is OK, but foo$bar.baz is not.

fix.column.names<-function(my.df){
  i <- 1
  for (name in colnames(my.df)) {
    new_name <- gsub("\\.", "_", name)
    names(my.df)[i] <- new_name
    i = i + 1
  }
  return (my.df)
}

# Extract data from a Netlogo BehaviourSpace experiment
read.nlogo.experiment <-
  function(path.name = "C:/Users/Weka/complexity/201804/Experiments",
           file.name = "take2 experiment-table.csv") {
    return (fix.column.names(
      read.table(
        file.path(path.name, file.name),
        header = T,
        sep = ",",
        skip = 6,
        quote = "\"",
        fill = TRUE
      ))) }

get.last.step.data <- function(my.df){
  return(my.df[my.df$X_step_ == max(my.df$X_step_), ])
} 

get.tau <-
  function (path.name="C:/Users/Weka/complexity/201804/Experiments",file.name="take2 experiment-table.csv") {
    return (get.last.step.data( read.nlogo.experiment(path.name,file.name)))
  }
  
extract.tau<-function(tau.data,can_borrow=TRUE,randomize_step=TRUE){
  mydata.canborrow <- if (can_borrow) "true" else "false"
  mydata.randomize_step <- if (randomize_step) "true" else "false"
  return (tau.data[tau.data$randomize_step==mydata.randomize_step&tau.data$can_borrow==mydata.canborrow,]) 
}

extract.step.data<-function(netlogo.data,can_borrow=TRUE,randomize_step=TRUE,tau=0,n_predictors=3,n_coefficients=3){
  mydata.canborrow <- if (can_borrow) "true" else "false"
  mydata.randomize_step <- if (randomize_step) "true" else "false"
  return (netlogo.data[netlogo.data$randomize_step==mydata.randomize_step & 
                         netlogo.data$can_borrow==mydata.canborrow &
                         netlogo.data$tau==tau &
                         netlogo.data$n_predictors==n_predictors &
                         netlogo.data$n_coefficients==n_coefficients,
                       ]) 
}

extract.wealth.vs.tau<-function(tau.data,can_borrow=TRUE,randomize_step=TRUE) {
  tau.data<-extract.tau(tau.data,can_borrow,randomize_step)
  tau.data.end<-tau.data[tau.data$X_step_==tau.data$n_ticks,]
  return (aggregate(tau.data.end,by=list(tau.data.end$tau),FUN=mean,na.rm=TRUE))
}

extract.errors.vs.tau<-function(tau.data,tau=0,can_borrow=TRUE,randomize_step=TRUE) {
  tau.data<-extract.tau(tau.data,can_borrow,randomize_step)
  return (tau.data[tau.data$tau==tau,])
}

# Get names of input parameters that have more than one value in experiment file
get.names.of.varying.parameters<-function(data,min_col=2,max_col=17) {
  is.varying<-function(name){
    return (nrow(unique(data[name]))>1)
  }
  return (Filter(is.varying,colnames(data)[min_col:max_col]))
}

# Get total number of combinations of input parameters values
get.n.configurations<-function(data) {
  product = 1
  for (name in get.names.of.varying.parameters(data)) {
    product = product * nrow(unique(data[name]))
  }
  return (product)
}

get.n.repetitions<-function(data){
  return (  length(unique(data$X_run_number_)) / get.n.configurations(data))
}

get.ns<-function(data){
  f<-function(name){toString(unique(data[name]))}
  return (lapply(get.configurations(data),f))
}

get.netlogo.values<-function(data){
  get.param.values<-function(name){
      values<-unique(data[name])[[1]]
      return (paste(values,collapse=", "))
    }
  return (lapply(get.names.of.varying.parameters(data),get.param.values))
}

get.netlogo.params<-function(data){
  return ( data.frame(get.names.of.varying.parameters(data),
                      unlist(get.netlogo.values(data))) )
}

plot.errors<-function(netlogo.data,can_borrow=TRUE,randomize_step=TRUE,tau=0,n_predictors=3,n_coefficients=3) {
  err<-extract.step.data(netlogo.data,can_borrow,randomize_step,tau,n_predictors,n_coefficients)
  rbPal <- colorRampPalette(c('red','blue'))
  err$Col <- rbPal(10)[as.numeric(cut(err$X_run_number_,breaks = 10))]
  plot(err$X_step_,err$mean__sum_squares_error__of_investors,
       xlab = "Step",ylab = "Squared error",pch=1,col=err$Col,
       main=sprintf("n_predictors=%d, n_coefficients=%d",n_predictors,n_coefficients))
}

plot.wealth<-function(netlogo.data,can_borrow=TRUE,randomize_step=TRUE,tau=0,n_predictors=3,n_coefficients=3) {
  err<-extract.step.data(netlogo.data,can_borrow,randomize_step,tau,n_predictors,n_coefficients)
  rbPal <- colorRampPalette(c('red','blue'))
  err$Col <- rbPal(10)[as.numeric(cut(err$X_run_number_,breaks = 10))]
  plot(err$X_step_,err$mean__wealth__of_investors,
       xlab = "Step",ylab = "Wealth",pch=1,col=err$Col,
       main=sprintf("n_predictors=%d, n_coefficients=%d",n_predictors,n_coefficients))
}

plot.outgoings<-function(netlogo.data,can_borrow=TRUE,randomize_step=TRUE,tau=0,n_predictors=3,n_coefficients=3) {
  err<-extract.step.data(netlogo.data,can_borrow,randomize_step,tau,n_predictors,n_coefficients)
  plot(err$X_step_,err$outgoings_POOL_HIGH,
       xlab = "Step",ylab = "Payout",pch=20,col="red",
       main=sprintf("n_predictors=%d, n_coefficients=%d",n_predictors,n_coefficients))
  points(err$X_step_,err$outgoings_POOL_LOW,pch=1,col="yellow")
  points(err$X_step_,err$outgoings_POOL_STABLE,pch=20,col="green")    
}

accumulate.wealth<-function(payoffs,choices,tau=1) {
  my.wealth<-0
  change.count<- -1
  last.choice<- -1
  calculate.wealth<-function(pay){
    assign('my.wealth', my.wealth+pay, inherits=TRUE)
    return (my.wealth)
  }
  count.changes<-function(choice){
    if (choice!=last.choice){
      assign('change.count',change.count+1,inherits = TRUE)
      assign('last.choice',choice,inherits = TRUE)
    }
    return (change.count)
  }
  receipts <- sapply(payoffs,calculate.wealth)
  costs <- sapply(choices,count.changes)
  return ( receipts - tau * costs)
}

plot.individuals<-function(my.details,n=3,my.strategy=0,col=c('blue','black','red'),sub=""){
  wealths<-subset(my.details,
                  step==max(my.details$step) & strategy==my.strategy,select=c('wealth','who','strategy'))
  wealths<-wealths[order(wealths$wealth),]
  N=length(wealths$wealth)
  n2 <- floor(N/2-n/2)
  exemplars<-wealths[c(1:n,n2:(n2+n-1),(N-n+1):N),]
  max.wealth <- round_any(max(wealths$wealth),10,f=ceiling)
  tau <- my.details$tau[1]
  plot(0:100,0:100, xlab = "Step",ylab = "Wealth",type='n',
       xlim=c(0,max(my.details$step)),ylim=c(0,max.wealth),
       main=sprintf('Growth of wealth for strategy=%d, tau=%d',my.strategy,tau),
       sub=sub)
  colours=c( rep(col[1],n), rep(col[2],n), rep(col[3],n) )
  for (who in exemplars$who) {
    plot.data<-my.details[my.details$who==who,]
    plot.data$extra<-accumulate.wealth(plot.data$payoffs,plot.data$choices)
    lines(plot.data$step,plot.data$extra,type='l',col=colours[1])
    colours<-colours[2:length(colours)]
  }
  legend('topleft',c("Lowest","Median","Best"),col=col,lty=1)
}

read.cartel <- function(path.name = "C:/Users/Weka/complexity/201804/Experiments", file.name = 'challenge-cartel-table.csv') {
  cartel.data<-fix.column.names( read.nlogo.experiment(path.name,file.name))
  return(cartel.data[cartel.data$X_step_ == max(cartel.data$X_step_), ])
}


plot.cartel<-function(cartel.data) {
  col=c('blue','red','black')
  my.data<-aggregate(cartel.data,by=list(cartel.data$tau,cartel.data$n_cartel),FUN=mean,na.rm=TRUE)
  plot(0:20,0:20, xlab = "Number in Cartel",ylab = "Average Return",type='n',
       xlim=c(0,max(cartel.data$n_cartel)),ylim=c(0,2),
       main="Cartel")
  i<-1
  for (tau in  unique(cartel.data$tau)){
    my.data.0<-my.data[my.data$tau==tau,]
    lines( my.data.0$n_cartel, my.data.0$outgoings_POOL_HIGH,type='l',col=col[i])
    i <- i + 1
  }
  lines( my.data.0$n_cartel, rep(1,length(my.data.0$n_cartel)),type='l',lty='dashed',col=col[i])
  legend('topleft',c("tau=0","tau=1","Stable Pool"),col=col,lty=c('solid','solid','dashed'))
}

plot.many.investors.pools<-function(many.investors.means,tau=0,p_experiencers=0.25) {
  my.data<- many.investors.means[many.investors.means$tau==tau &
                                   many.investors.means$p_experiencers==p_experiencers,]
  max.census=max(c(max(my.data$census_POOL_STABLE),
                   max(my.data$census_POOL_LOW),
                   max(my.data$census_POOL_LOW)))
  plot(100:500,100:500,type='n', 
       xlim=c(min(many.investors.means$n_investors),max(many.investors.means$n_investors)),
       ylim=c(0,max.census),
       xlab="Number of Investors",ylab = "Number in pool",
       main=sprintf("tau=%d, experiencers=%.0f%%",tau,100*p_experiencers))
  lines( my.data$n_investors, my.data$census_POOL_STABLE,type='l',col="green")
  lines( my.data$n_investors, my.data$census_POOL_LOW,type='l',col="yellow")
  lines( my.data$n_investors, my.data$census_POOL_HIGH,type='l',col="red")
  lines( my.data$n_investors, rep(20,length(my.data$n_investors),type='l',lty='dashed',col='grey'))
  legend('topleft',
         c("Stable","Low","High","profitable"),col=c("green","yellow","red","grey"),
         lty=c('solid','solid','solid','dashed'))
}

analyze.ergodicity<-function(ergodic.data,
                             cols=c("X_run_number_",
                                   "p_start_low",
                                   "p_start_high",
                                   "X_step_",
                                   "tau",
                                    "census_POOL_STABLE",
                                    "census_POOL_LOW",
                                    "census_POOL_HIGH"),
                             n=7,
                             nsigma=1.0,
                             tau=1,
                             max.count=3) {
  ergodic.data.reduced<-ergodic.data[
                          ergodic.data$p_start_low+ergodic.data$p_start_high<=1.0 & ergodic.data$tau==tau,
                          cols]
 
  colnames(ergodic.data.reduced)=cols
  my.means<-aggregate( ergodic.data.reduced,
                       by=list( ergodic.data.reduced$X_run_number_,
                                ergodic.data.reduced$p_start_low,
                                ergodic.data.reduced$p_start_high),
                       FUN=mean,
                       na.rm=TRUE)
 
  my.sigmas<-aggregate( ergodic.data.reduced,
                       by=list( ergodic.data.reduced$X_run_number_,
                                ergodic.data.reduced$p_start_low,
                                ergodic.data.reduced$p_start_high),
                       FUN=sd,
                       na.rm=TRUE)

  joined<-merge(my.means,my.sigmas,by=c("Group.1","Group.2","Group.3"))
  is.within.limits<-function(low,x,y) {return (low <x && x < y) }
  
  results<-list()
  for (i in 1:nrow(joined)) {
    rolling.averages<-get.rolling.averages(ergodic.data.reduced,joined[i,4],joined[i,5],joined[i,6],n=n)
    stable.pool0 <- joined$census_POOL_STABLE.x - nsigma * joined$census_POOL_STABLE.y
    stable.pool1 <- joined$census_POOL_STABLE.x + nsigma * joined$census_POOL_HIGH.y
    low.pool0    <- joined$census_POOL_LOW.x - nsigma * joined$census_POOL_LOW.y
    low.pool1    <- joined$census_POOL_LOW.x + nsigma * joined$census_POOL_LOW.y
    high.pool0   <- joined$census_POOL_HIGH.x - nsigma * joined$census_POOL_HIGH.y
    high.pool1   <- joined$census_POOL_HIGH.x + nsigma * joined$census_POOL_HIGH.y
    first = -1
    count = 0
    for (j in 1:nrow(rolling.averages)){
      if (is.within.limits(stable.pool0, rolling.averages$Stable[j],stable.pool1) &&
          is.within.limits(low.pool0, rolling.averages$Low[j],low.pool1) &&
          is.within.limits(high.pool0, rolling.averages$High[j],high.pool1)) {
        if (first == -1) {
          first = j
          count = 0
        } 
      } else {
        count = count + 1
        if (count > max.count) {
          first = -1
        }
        
      }
    }
    
    results<-append(results,if (first>0) first+floor(n/2) else nrow(rolling.averages)+floor(n/2))
 
  }
  joined$onset<-results
#  as.numeric(as.character(joined$onset))
  return (joined)
}



get.rolling.averages<-function(ergodic.data.reduced,key1,key2,key3,eps=0.001,n=7){
  mav <- function(x,n){filter(x,rep(1/n,n), sides=2)}
  one.run.data <- ergodic.data.reduced[abs(ergodic.data.reduced$X_run_number -  key1) < eps &
                                         abs(ergodic.data.reduced$p_start_low - key2) < eps &
                                         abs(ergodic.data.reduced$p_start_high - key3) < eps, ]
  averages <- data.frame(
    mav(one.run.data$census_POOL_STABLE, n),
    mav(one.run.data$census_POOL_LOW, n),
    mav(one.run.data$census_POOL_HIGH, n)
  )
  colnames(averages) <- c("Stable", "Low", "High")
  return (na.omit(averages))
}
 