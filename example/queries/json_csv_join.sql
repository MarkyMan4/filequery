select
    t.*,
    j.nested.nest_id,
    j.nested.nest_id
from 
    test t
    inner join json_test j
    on t.col1 = j.id