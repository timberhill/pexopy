
# timing_plot.R
# write the text file
utc1 <- as.character(utc[,1])
utc2 <- as.character(utc[,2])
csv_table = data.frame(utc1,utc2, bjd.tdb) # JDUTC + BJDTDB
print("Saving timing to: ")
print(gsub(".pdf", ".csv", fout))
write.table(csv_table, file=gsub(".pdf", ".csv", fout),
    col.names=c("JDUTC_base","JDUTC_fraction","BJDTDB_base","BJDTDB_fraction"), row.names=FALSE, na="NaN", sep="\t", quote=FALSE)


# pexo.R
options(digits=20) # needed, I think
utc_old <- cbind(2450000,seq(0,10000,by=0.1)) # step of 0.1 days

utc <- cbind(seq(2450000,2460000,by=1),runif(1e4,0,1)) # random step


# more pexo.R
########################################
###global Settings
########################################
df <- 0
tbase <- 1
#dt <- 0
test.type <- 'real'
Norder <- 3
type <- 'uniform'
CLK <- ''
eopType <- '00B'
#eopType <- 'approx'
# eopType <- '06'
#TT.standard <- 'BIPM17'
TT.standard <- 'BIPM16'
#TT.standard <- 'TAI'
#TT.standard <- 'UNCORR'
UNITS <- 'TDB'
DE <- 430
verbose <-TRUE
comparison <- TRUE
plotf <-TRUE