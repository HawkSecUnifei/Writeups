# web challenge solved with JWT injection


if u read the code u can see that u receive a SESSION COOKIE when log in. Then to get the flag was needed to access /image/ben10 but with the cookie session of admin, then I just uso flask_unsign tool to brute force session token secret key, then signed again with the 'your_secret_key' that was the key that i found.

srdnlen{b3n_l0v3s_br0k3n_4cc355_c0ntr0l_vulns}

### sorry about the worst english ever :)
