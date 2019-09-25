if (!require('entropy')){
  install.packages('entropy')
  library('entropy')
}

my.path  <- '~/../complexity/it'
raw.data <- read.csv(file.path(my.path,'santafe-temps.csv'))
X        <- unlist(lapply(raw.data$MaxTemp,function(t) {return (if (t>=80) 1 else 0)}))
Y        <- unlist(lapply(raw.data$Precipation,function(p) {return (if(p>0) 1 else 0)}))

print (sprintf('I(X)=%.3f,I(X)=%.3f',
               entropy(discretize(X,numBins = 2),unit='log2'),
              entropy(discretize(Y,numBins = 2),unit='log2')))
XY = discretize2d(X,Y,numBins1 = 2,numBins2 = 2)
print(entropy(XY,unit='log2'))
