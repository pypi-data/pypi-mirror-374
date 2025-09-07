# Pyhatodi

**Pyhatodi** (from *hatodi* = "small hammer" in Hindi) is a lightweight developer toolkit designed to help Python developers with everyday tasks—locally and securely.  

> **Why Pyhatodi?**  
> Many developers use online tools for quick debugging tasks like decoding JWT tokens, risking exposure of sensitive information. Pyhatodi brings these utilities to your local machine, ensuring privacy and speed.

---

## Features

- **JWT Token Decoder**  
  Decode JSON Web Tokens (JWT) locally without sending them to any third-party service.  
  - Extracts and displays header and payload in a human-readable format.
  - No need to share tokens online.

More tools coming soon!

---

## Installation
```pip install pyhatodi```


## Usage
```pyhatodi jwt decode <your_jwt_token>```


```pyhatodi b64 encode <text to encode in base64>```


```pyhatodi b64 decode <base64 encoded string>```



## Why Local?
Avoid leaking sensitive tokens to online decoders.
Works completely offline.
Lightweight and fast.

## Roadmap
JSON/YAML formatter & validator
Base64 encoder/decoder
HTTP request tester 
Mock server generator

## Installation (development)

Clone the repository and install locally (development mode):

```bash
git clone https://github.com/gaikwad411/pyhatodi.git
cd pyhatodi
pip install -e .
```

