# Remote Code Execution Design Document (R.C.E.D.D)

The `authenticate.py` module is used for the **R.C.E**.
Therefore automatically fetching the `SECRET` constant from the web application using regex,
as well as parsing the **URL** to check for the scheme should not be **in** the `authenticate()` function.

The required parameters for the request will be obtained 
```py
authenticate(url: str, parameters: dict)
```
