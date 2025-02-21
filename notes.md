### Current state
- Only Class, function and method definitions and calls are modeled.
- Files are stored as node properties

### To-Do
- Add import path information for the LLM to know where new functionalities would have to be imported. This may not be necessary for experts (that know about __init__.py imports). Also the LLM might know how to handle it.