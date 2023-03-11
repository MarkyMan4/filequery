-- queries nested JSON which DuckDB interprets as a struct
select 
    nested.nest_id,
    nested.nest_val
from json_test;
