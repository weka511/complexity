setwd ("C:/Users/Weka/201804/Experiments")
my.df<-read.table("take2 experiment-table.csv",
                  header = T,   # set columns names true
                  sep = ",",    # define the separator between       columns
                  skip = 6,     # skip first 6 rows 
                  quote = "\"", # correct the column separator
                  fill = TRUE ) # add blank fields if rows

