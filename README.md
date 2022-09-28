# The Vial Project

<p align="center">
    <a href="https://github.com/CopernicusPY/vial/stargazers"><img src="https://img.shields.io/github/stars/CopernicusPY/vial?colorA=363a4f&colorB=b7bdf8&style=for-the-badge"></a>
    <a href="https://github.com/CopernicusPY/vial/issues"><img src="https://img.shields.io/github/issues/CopernicusPY/vial?colorA=363a4f&colorB=f5a97f&style=for-the-badge"></a>
    <a href="https://github.com/CopernicusPY/vial/contributors"><img src="https://img.shields.io/github/contributors/CopernicusPY/vial?colorA=363a4f&colorB=a6da95&style=for-the-badge"></a>
</p>

## About

Vial is a `lightweight python framework` focused on exploiting [Flask](https://flask.palletsprojects.com/) applications. <br>
It allows efficient session cookie ["forging"](https://en.wikipedia.org/wiki/Session_hijacking) and decoding (Can be useful for understanding the applications structure). <br>
It also makes it possible to bruteforce [session](https://flask.palletsprojects.com/en/2.2.x/quickstart/#sessions) keys. <br>

### Introducing: Remote Code Execution

**Vial**'s new feature is the remote code execution utility that abused [Werkzeug](https://werkzeug.palletsprojects.com/)'s [debug console](https://werkzeug.palletsprojects.com/en/2.2.x/debug/), when left activated in a production environment. <br>
The debugger's console is sometimes protected by a PIN which is generated in the servers side in a [deterministic](https://en.wikipedia.org/wiki/Deterministic_algorithm) way using a combination of public and possibly private information of the server/website project itself. <br>
To reverse the PIN these "secret" and "public" bits are required, although can be obtained by exploiting other vulnerabilities such as **arbitary file read** or through **phishing campaigns** (less common). <br>
**Vial** also accepts already obtained application PIN's. <br>
After collecting the PIN it sends a malicious request to the target forcing him to connect to a previously started TCP Server giving the attacker a shell. <br>
(This can be achieved through manually interacting with the web browser although its better to just stay in your terminal isn't it?)

