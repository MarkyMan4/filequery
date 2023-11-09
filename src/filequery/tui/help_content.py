help_md = """\
# Help

controls

|key|action|
|---|------|
|ctrl+c|quit|
|f2|toggle help screen|
|f9|execute SQL in the editor|
|ctrl+q|save editor content|
|ctrl+r|save result|

---

editor controls

|key|action|
|---|------|
|escape|focus on the next item|
|up|move the cursor up|
|down|move the cursor down|
|left|move the cursor left|
|ctrl+left|move the cursor to the start of the word|
|ctrl+shift+left|move the cursor to the start of the word and select|
|right|move the cursor right|
|ctrl+right|move the cursor to the end of the word|
|ctrl+shift+right|move the cursor to the end of the word and select|
|home,ctrl+a|move the cursor to the start of the line|
|end,ctrl+e|move the cursor to the end of the line|
|shift+home|move the cursor to the start of the line and select|
|shift+end|move the cursor to the end of the line and select|
|pageup|move the cursor one page up|
|pagedown|move the cursor one page down|
|shift+up|select while moving the cursor up|
|shift+down|select while moving the cursor down|
|shift+left|select while moving the cursor left|
|shift+right|select while moving the cursor right|
|backspace|delete character to the left of cursor|
|ctrl+w|delete from cursor to start of the word|
|delete,ctrl+d|delete character to the right of cursor|
|ctrl+f|delete from cursor to end of the word|
|ctrl+x|delete the current line|
|ctrl+u|delete from cursor to the start of the line|
|ctrl+k|delete from cursor to the end of the line|
|f6|select the current line|
|f7|select all text in the document|

helpful SQL statements

```sql
show tables; # list tables in the database
describe table <table name>; # get information about the columns in a table
```
"""
