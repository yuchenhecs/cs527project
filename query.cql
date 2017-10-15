
--this works
select * from "metrics"."app_36437104577c4432_calculateMetrics" where application='application--1792657053' and session='X5' and user='user-1375724504'; 

--this does not work, giving the error described, something related to json encoding
select json * from "metrics"."app_36437104577c4432_calculateMetrics" where application='application--1792657053' and session='X5' and user='user-1375724504'; 
