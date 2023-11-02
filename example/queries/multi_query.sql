select *
from test;

select *
from test1;

select *
from 
    test t1
    inner join test1 t2
    on t1.col1 = t2.col1;
