# Top 10 from optimization (2025-10-03)

## 1. optimization_self_improvement_2025-07-30.md_20250924_204925.md

# Agent Self-Improvement Log
Date: 2025-07-30

## Actions Taken:
- Detected missing heartbeats for: 2025-07-29, 2025-07-28, 2025-07-27, 2025-07-26, 2025-07-25, 2025-07-24, 2025-07-23. Will adjust scheduler logic.
- Performed log cleanup and optimized agent execution order.

## 2. optimization_README.md_20250924_204924.md

# Forge

[![npm package](https://nodei.co/npm/node-forge.png?downloads=true&downloadRank=true&stars=true)](https://nodei.co/npm/node-forge/)

[![Build Status](https://github.com/digitalbazaar/forge/workflows/Main%20Checks/badge.svg)](https://github.com/digitalbazaar/forge/actions?query=workflow%3A%22Main+Checks%22)

A native implementation of [TLS][] (and various other cryptographic tools) in
[JavaScript][].

Introduction
------------

The Forge software is a fully native implementation of the [TLS][] protocol
in JavaScript, a set of cryptography utilities, and a set of tools for
developing Web Apps that utilize many network resources.

Performance
------------

Forge is fast. Benchmarks against other popular JavaScript cryptography
libraries can be found here:

* http://dominictarr.github.io/crypto-bench/
* http://cryptojs.altervista.org/test/simulate-threading-speed_test.html

Documentation
-------------

* [Introduction](#introduction)
* [Performance](#performance)
* [Installation](#installation)
* [Testing](#testing)
* [Contributing](#contributing)

### API

* [Options](#options)

### Transports

* [TLS](#tls)
* [HTTP](#http)
* [SSH](#ssh)
* [XHR](#xhr)
* [Sockets](#socket)

### Ciphers

* [CIPHER](#cipher)
* [AES](#aes)
* [DES](#des)
* [RC2](#rc2)

### PKI

* [ED25519](#ed25519)
* [RSA](#rsa)
* [RSA-KEM](#rsakem)
* [X.509](#x509)
* [PKCS#5](#pkcs5)
* [PKCS#7](#pkcs7)
* [PKCS#8](#pkcs8)
* [PKCS#10](#pkcs10)
* [PKCS#12](#pkcs12)
* [ASN.1](#asn)

### Message Digests

* [SHA1](#sha1)
* [SHA256](#sha256)
* [SHA384](#sha384)
* [SHA512](#sha512)
* [MD5](#md5)
* [HMAC](#hmac)

### Utilities

* [Prime](#prime)
* [PRNG](#prng)
* [Tasks](#task)
* [Utilities](#util)
* [Logging](#log)
* [Flash Networking Support](#flash)

### Other

* [Security Considerations](#security-considerations)
* [Library Background](#library-background)
* [Contact](#contact)
* [Donations](#donations)

---------------------------------------

Installation
------------

**Note**: Please see the [Security Considerations](#security-considerations)
section before using packaging systems and pre-built files.

Forge uses a [CommonJS][] module structure with a build process for browser
bundles. The older [0.6.x][] branch with standalone files is available but will
not be regularly updated.

### Node.js

If you want to use forge with [Node.js][], it is available through `npm`:

https://www.npmjs.com/package/node-forge

Installation:

    npm install node-forge

You can then use forge as a regular module:

```js
var forge = require('node-forge');
```

The npm package includes pre-built `forge.min.js`, `forge.all.min.js`, and
`prime.worker.min.js` using the [UMD][] format.

### jsDelivr CDN

To use it via [jsDelivr](https://www.jsdelivr.com/package/npm/node-forge) include this in your html:

```html
<script src="https://cdn.jsdelivr.net/npm/node-forge@1.0.0/dist/forge.min.js"></script>
```

### unpkg CDN

To use it via [unpkg](https://unpkg.com/#/) include this in your html:

```html
<script src="https://unpkg.com/node-forge@1.0.0/dist/forge.min.js"></script>
```

### Development Requirements

The core JavaScript has the following requirements to build and test:

* Building a browser bundle:
  * Node.js
  * npm
* Testing
  * Node.js
  * npm
  * Chrome, Firefox, Safari (optional)

Some special networking features can optionally use a Flash component.  See the
[Flash README](./flash/README.md) for details.

### Building for a web browser

To create single file bundles for use with browsers run the following:

    npm install
    npm run build

This will create single non-minimized and minimized files that can be
included in the browser:

    dist/forge.js
    dist/forge.min.js

A bundle that adds some utilities and networking support is also available:

    dist/forge.all.js
    dist/forge.all.min.js

Include the file via:

```html
<script src="YOUR_SCRIPT_PATH/forge.js"></script>
```
or
```html
<script src="YOUR_SCRIPT_PATH/forge.min.js"></script>
```

The above bundles will synchronously create a global 'forge' object.

**Note**: These bundles will not include any WebWorker scripts (eg:
`dist/prime.worker.js`), so these will need to be accessible from the browser
if any WebWorkers are used.

### Building a custom browser bundle

The build process uses [webpack][] and the [config](./webpack.config.js) file
can be modified to generate a file or files that only contain the parts of
forge you need.

[Browserify][] override support is also present in `package.json`.

Testing
-------

### Prepare to run tests

    npm install

### Running automated tests with Node.js

Forge natively runs in a [Node.js][] environment:

    npm test

### Running automated tests with Headless Chrome

Automated testing is done via [Karma][]. By default it will run the tests with
Headless Chrome.

    npm run test-karma

Is 'mocha' reporter output too verbose? Other reporters are available. Try
'dots', 'progress', or 'tap'.

    npm run test-karma -- --reporters progress

By default [webpack][] is used. [Browserify][] can also be used.

    BUNDLER=browserify npm run test-karma

### Running automated tests with one or more browsers

You can also specify one or more browsers to use.

    npm run test-karma -- --browsers Chrome,Firefox,Safari,ChromeHeadless

The reporter option and `BUNDLER` environment variable can also be used.

### Running manual tests in a browser

Testing in a browser uses [webpack][] to combine forge and all tests and then
loading the result in a browser. A simple web server is provided that will
output the HTTP or HTTPS URLs to load. It also will start a simple Flash Policy
Server. Unit tests and older legacy tests are provided. Custom ports can be
used by running `node tests/server.js` manually.

To run the unit tests in a browser a special forge build is required:

    npm run test-build

To run legacy browser based tests the main forge build is required:

    npm run build

The tests are run with a custom server that prints out the URLs to use:

    npm run test-server

### Running other tests

There are some other random tests and benchmarks available in the tests
directory.

### Coverage testing

To perform coverage testing of the unit tests, run the following. The results
will be put in the `coverage/` directory. Note that coverage testing can slow
down some tests considerably.

    npm install
    npm run coverage

Contributing
------------

Any contributions (eg: PRs) that are accepted will be brought under the same
license used by the rest of the Forge project. This license allows Forge to
be used under the terms of either the BSD License or the GNU General Public
License (GPL) Version 2.

See: [LICENSE](https://github.com/digitalbazaar/forge/blob/cbebca3780658703d925b61b2caffb1d263a6c1d/LICENSE)

If a contribution contains 3rd party source code with its own license, it
may retain it, so long as that license is compatible with the Forge license.

API
---

<a name="options" />

### Options

If at any time you wish to disable the use of native code, where available,
for particular forge features like its secure random number generator, you
may set the ```forge.options.usePureJavaScript``` flag to ```true```. It is
not recommended that you set this flag as native code is typically more
performant and may have stronger security properties. It may be useful to
set this flag to test certain features that you plan to run in environments
that are different from your testing environment.

To disable native code when including forge in the browser:

```js
// run this *after* including the forge script
forge.options.usePureJavaScript = true;
```

To disable native code when using Node.js:

```js
var forge = require('node-forge');
forge.options.usePureJavaScript = true;
```

Transports
----------

<a name="tls" />

### TLS

Provides a native javascript client and server-side [TLS][] implementation.

__Examples__

```js
// create TLS client
var client = forge.tls.createConnection({
  server: false,
  caStore: /* Array of PEM-formatted certs or a CA store object */,
  sessionCache: {},
  // supported cipher suites in order of preference
  cipherSuites: [
    forge.tls.CipherSuites.TLS_RSA_WITH_AES_128_CBC_SHA,
    forge.tls.CipherSuites.TLS_RSA_WITH_AES_256_CBC_SHA],
  virtualHost: 'example.com',
  verify: function(connection, verified, depth, certs) {
    if(depth === 0) {
      var cn = certs[0].subject.getField('CN').value;
      if(cn !== 'example.com') {
        verified = {
          alert: forge.tls.Alert.Description.bad_certificate,
          message: 'Certificate common name does not match hostname.'
        };
      }
    }
    return verified;
  },
  connected: function(connection) {
    console.log('connected');
    // send message to server
    connection.prepare(forge.util.encodeUtf8('Hi server!'));
    /* NOTE: experimental, start heartbeat retransmission timer
    myHeartbeatTimer = setInterval(function() {
      connection.prepareHeartbeatRequest(forge.util.createBuffer('1234'));
    }, 5*60*1000);*/
  },
  /* provide a client-side cert if you want
  getCertificate: function(connection, hint) {
    return myClientCertificate;
  },
  /* the private key for the client-side cert if provided */
  getPrivateKey: function(connection, cert) {
    return myClientPrivateKey;
  },
  tlsDataReady: function(connection) {
    // TLS data (encrypted) is ready to be sent to the server
    sendToServerSomehow(connection.tlsData.getBytes());
    // if you were communicating with the server below, you'd do:
    // server.process(connection.tlsData.getBytes());
  },
  dataReady: function(connection) {
    // clear data from the server is ready
    console.log('the server sent: ' +
      forge.util.decodeUtf8(connection.data.getBytes()));
    // close connection
    connection.close();
  },
  /* NOTE: experimental
  heartbeatReceived: function(connection, payload) {
    // restart retransmission timer, look at payload
    clearInterval(myHeartbeatTimer);
    myHeartbeatTimer = setInterval(function() {
      connection.prepareHeartbeatRequest(forge.util.createBuffer('1234'));
    }, 5*60*1000);
    payload.getBytes();
  },*/
  closed: function(connection) {
    console.log('disconnected');
  },
  error: function(connection, error) {
    console.log('uh oh', error);
  }
});

// start the handshake process
client.handshake();

// when encrypted TLS data is received from the server, process it
client.process(encryptedBytesFromServer);

// create TLS server
var server = forge.tls.createConnection({
  server: true,
  caStore: /* Array of PEM-formatted certs or a CA store object */,
  sessionCache: {},
  // supported cipher suites in order of preference
  cipherSuites: [
    forge.tls.CipherSuites.TLS_RSA_WITH_AES_128_CBC_SHA,
    forge.tls.CipherSuites.TLS_RSA_WITH_AES_256_CBC_SHA],
  // require a client-side certificate if you want
  verifyClient: true,
  verify: function(connection, verified, depth, certs) {
    if(depth === 0) {
      var cn = certs[0].subject.getField('CN').value;
      if(cn !== 'the-client') {
        verified = {
          alert: forge.tls.Alert.Description.bad_certificate,
          message: 'Certificate common name does not match expected client.'
        };
      }
    }
    return verified;
  },
  connected: function(connection) {
    console.log('connected');
    // send message to client
    connection.prepare(forge.util.encodeUtf8('Hi client!'));
    /* NOTE: experimental, start heartbeat retransmission timer
    myHeartbeatTimer = setInterval(function() {
      connection.prepareHeartbeatRequest(forge.util.createBuffer('1234'));
    }, 5*60*1000);*/
  },
  getCertificate: function(connection, hint) {
    return myServerCertificate;
  },
  getPrivateKey: function(connection, cert) {
    return myServerPrivateKey;
  },
  tlsDataReady: function(connection) {
    // TLS data (encrypted) is ready to be sent to the client
    sendToClientSomehow(connection.tlsData.getBytes());
    // if you were communicating with the client above you'd do:
    // client.process(connection.tlsData.getBytes());
  },
  dataReady: function(connection) {
    // clear data from the client is ready
    console.log('the client sent: ' +
      forge.util.decodeUtf8(connection.data.getBytes()));
    // close connection
    connection.close();
  },
  /* NOTE: experimental
  heartbeatReceived: function(connection, payload) {
    // restart retransmission timer, look at payload
    clearInterval(myHeartbeatTimer);
    myHeartbeatTimer = setInterval(function() {
      connection.prepareHeartbeatRequest(forge.util.createBuffer('1234'));
    }, 5*60*1000);
    payload.getBytes();
  },*/
  closed: function(connection) {
    console.log('disconnected');
  },
  error: function(connection, error) {
    console.log('uh oh', error);
  }
});

// when encrypted TLS data is received from the client, process it
server.process(encryptedBytesFromClient);
```

Connect to a TLS server using node's net.Socket:

```js
var socket = new net.Socket();

var client = forge.tls.createConnection({
  server: false,
  verify: function(connection, verified, depth, certs) {
    // skip verification for testing
    console.log('[tls] server certificate verified');
    return true;
  },
  connected: function(connection) {
    console.log('[tls] connected');
    // prepare some data to send (note that the string is interpreted as
    // 'binary' encoded, which works for HTTP which only uses ASCII, use
    // forge.util.encodeUtf8(str) otherwise
    client.prepare('GET / HTTP/1.0\r\n\r\n');
  },
  tlsDataReady: function(connection) {
    // encrypted data is ready to be sent to the server
    var data = connection.tlsData.getBytes();
    socket.write(data, 'binary'); // encoding should be 'binary'
  },
  dataReady: function(connection) {
    // clear data from the server is ready
    var data = connection.data.getBytes();
    console.log('[tls] data received from the server: ' + data);
  },
  closed: function() {
    console.log('[tls] disconnected');
  },
  error: function(connection, error) {
    console.log('[tls] error', error);
  }
});

socket.on('connect', function() {
  console.log('[socket] connected');
  client.handshake();
});
socket.on('data', function(data) {
  client.process(data.toString('binary')); // encoding should be 'binary'
});
socket.on('end', function() {
  console.log('[socket] disconnected');
});

// connect to google.com
socket.connect(443, 'google.com');

// or connect to gmail's imap server (but don't send the HTTP header above)
//socket.connect(993, 'imap.gmail.com');
```

<a name="http" />

### HTTP

Provides a native [JavaScript][] mini-implementation of an http client that
uses pooled sockets.

__Examples__

```js
// create an HTTP GET request
var request = forge.http.createRequest({method: 'GET', path: url.path});

// send the request somewhere
sendSomehow(request.toString());

// receive response
var buffer = forge.util.createBuffer();
var response = forge.http.createResponse();
var someAsyncDataHandler = function(bytes) {
  if(!response.bodyReceived) {
    buffer.putBytes(bytes);
    if(!response.headerReceived) {
      if(response.readHeader(buffer)) {
        console.log('HTTP response header: ' + response.toString());
      }
    }
    if(response.headerReceived && !response.bodyReceived) {
      if(response.readBody(buffer)) {
        console.log('HTTP response body: ' + response.body);
      }
    }
  }
};
```

<a name="ssh" />

### SSH

Provides some SSH utility functions.

__Examples__

```js
// encodes (and optionally encrypts) a private RSA key as a Putty PPK file
forge.ssh.privateKeyToPutty(privateKey, passphrase, comment);

// encodes a public RSA key as an OpenSSH file
forge.ssh.publicKeyToOpenSSH(key, comment);

// encodes a private RSA key as an OpenSSH file
forge.ssh.privateKeyToOpenSSH(privateKey, passphrase);

// gets the SSH public key fingerprint in a byte buffer
forge.ssh.getPublicKeyFingerprint(key);

// gets a hex-encoded, colon-delimited SSH public key fingerprint
forge.ssh.getPublicKeyFingerprint(key, {encoding: 'hex', delimiter: ':'});
```

<a name="xhr" />

### XHR

Provides an XmlHttpRequest implementation using forge.http as a backend.

__Examples__

```js
// TODO
```

<a name="socket" />

### Sockets

Provides an interface to create and use raw sockets provided via Flash.

__Examples__

```js
// TODO
```

Ciphers
-------

<a name="cipher" />

### CIPHER

Provides a basic API for block encryption and decryption. There is built-in
support for the ciphers: [AES][], [3DES][], and [DES][], and for the modes
of operation: [ECB][], [CBC][], [CFB][], [OFB][], [CTR][], and [GCM][].

These algorithms are currently supported:

* AES-ECB
* AES-CBC
* AES-CFB
* AES-OFB
* AES-CTR
* AES-GCM
* 3DES-ECB
* 3DES-CBC
* DES-ECB
* DES-CBC

When using an [AES][] algorithm, the key size will determine whether
AES-128, AES-192, or AES-256 is used (all are supported). When a [DES][]
algorithm is used, the key size will determine whether [3DES][] or regular
[DES][] is used. Use a [3DES][] algorithm to enforce Triple-DES.

__Examples__

```js
// generate a random key and IV
// Note: a key size of 16 bytes will use AES-128, 24 => AES-192, 32 => AES-256
var key = forge.random.getBytesSync(16);
var iv = forge.random.getBytesSync(16);

/* alternatively, generate a password-based 16-byte key
var salt = forge.random.getBytesSync(128);
var key = forge.pkcs5.pbkdf2('password', salt, numIterations, 16);
*/

// encrypt some bytes using CBC mode
// (other modes include: ECB, CFB, OFB, CTR, and GCM)
// Note: CBC and ECB modes use PKCS#7 padding as default
var cipher = forge.cipher.createCipher('AES-CBC', key);
cipher.start({iv: iv});
cipher.update(forge.util.createBuffer(someBytes));
cipher.finish();
var encrypted = cipher.output;
// outputs encrypted hex
console.log(encrypted.toHex());

// decrypt some bytes using CBC mode
// (other modes include: CFB, OFB, CTR, and GCM)
var decipher = forge.cipher.createDecipher('AES-CBC', key);
decipher.start({iv: iv});
decipher.update(encrypted);
var result = decipher.finish(); // check 'result' for true/false
// outputs decrypted hex
console.log(decipher.output.toHex());

// decrypt bytes using CBC mode and streaming
// Performance can suffer for large multi-MB inputs due to buffer
// manipulations. Stream processing in chunks can offer significant
// improvement. CPU intensive update() calls could also be performed with
// setImmediate/setTimeout to avoid blocking the main browser UI thread (not
// shown here). Optimal block size depends on the JavaScript VM and other
// factors. Encryption can use a simple technique for increased performance.
var encryptedBytes = encrypted.bytes();
var decipher = forge.cipher.createDecipher('AES-CBC', key);
decipher.start({iv: iv});
var length = encryptedBytes.length;
var chunkSize = 1024 * 64;
var index = 0;
var decrypted = '';
do {
  decrypted += decipher.output.getBytes();
  var buf = forge.util.createBuffer(encryptedBytes.substr(index, chunkSize));
  decipher.update(buf);
  index += chunkSize;
} while(index < length);
var result = decipher.finish();
assert(result);
decrypted += decipher.output.getBytes();
console.log(forge.util.bytesToHex(decrypted));

// encrypt some bytes using GCM mode
var cipher = forge.cipher.createCipher('AES-GCM', key);
cipher.start({
  iv: iv, // should be a 12-byte binary-encoded string or byte buffer
  additionalData: 'binary-encoded string', // optional
  tagLength: 128 // optional, defaults to 128 bits
});
cipher.update(forge.util.createBuffer(someBytes));
cipher.finish();
var encrypted = cipher.output;
var tag = cipher.mode.tag;
// outputs encrypted hex
console.log(encrypted.toHex());
// outputs authentication tag
console.log(tag.toHex());

// decrypt some bytes using GCM mode
var decipher = forge.cipher.createDecipher('AES-GCM', key);
decipher.start({
  iv: iv,
  additionalData: 'binary-encoded string', // optional
  tagLength: 128, // optional, defaults to 128 bits
  tag: tag // authentication tag from encryption
});
decipher.update(encrypted);
var pass = decipher.finish();
// pass is false if there was a failure (eg: authentication tag didn't match)
if(pass) {
  // outputs decrypted hex
  console.log(decipher.output.toHex());
}
```

Using forge in Node.js to match openssl's "enc" command line tool (**Note**: OpenSSL "enc" uses a non-standard file format with a custom key derivation function and a fixed iteration count of 1, which some consider less secure than alternatives such as [OpenPGP](https://tools.ietf.org/html/rfc4880)/[GnuPG](https://www.gnupg.org/)):

```js
var forge = require('node-forge');
var fs = require('fs');

// openssl enc -des3 -in input.txt -out input.enc
function encrypt(password) {
  var input = fs.readFileSync('input.txt', {encoding: 'binary'});

  // 3DES key and IV sizes
  var keySize = 24;
  var ivSize = 8;

  // get derived bytes
  // Notes:
  // 1. If using an alternative hash (eg: "-md sha1") pass
  //   "forge.md.sha1.create()" as the final parameter.
  // 2. If using "-nosalt", set salt to null.
  var salt = forge.random.getBytesSync(8);
  // var md = forge.md.sha1.create(); // "-md sha1"
  var derivedBytes = forge.pbe.opensslDeriveBytes(
    password, salt, keySize + ivSize/*, md*/);
  var buffer = forge.util.createBuffer(derivedBytes);
  var key = buffer.getBytes(keySize);
  var iv = buffer.getBytes(ivSize);

  var cipher = forge.cipher.createCipher('3DES-CBC', key);
  cipher.start({iv: iv});
  cipher.update(forge.util.createBuffer(input, 'binary'));
  cipher.finish();

  var output = forge.util.createBuffer();

  // if using a salt, prepend this to the output:
  if(salt !== null) {
    output.putBytes('Salted__'); // (add to match openssl tool output)
    output.putBytes(salt);
  }
  output.putBuffer(cipher.output);

  fs.writeFileSync('input.enc', output.getBytes(), {encoding: 'binary'});
}

// openssl enc -d -des3 -in input.enc -out input.dec.txt
function decrypt(password) {
  var input = fs.readFileSync('input.enc', {encoding: 'binary'});

  // parse salt from input
  input = forge.util.createBuffer(input, 'binary');
  // skip "Salted__" (if known to be present)
  input.getBytes('Salted__'.length);
  // read 8-byte salt
  var salt = input.getBytes(8);

  // Note: if using "-nosalt", skip above parsing and use
  // var salt = null;

  // 3DES key and IV sizes
  var keySize = 24;
  var ivSize = 8;

  var derivedBytes = forge.pbe.opensslDeriveBytes(
    password, salt, keySize + ivSize);
  var buffer = forge.util.createBuffer(derivedBytes);
  var key = buffer.getBytes(keySize);
  var iv = buffer.getBytes(ivSize);

  var decipher = forge.cipher.createDecipher('3DES-CBC', key);
  decipher.start({iv: iv});
  decipher.update(input);
  var result = decipher.finish(); // check 'result' for true/false

  fs.writeFileSync(
    'input.dec.txt', decipher.output.getBytes(), {encoding: 'binary'});
}
```

<a name="aes" />

### AES

Provides [AES][] encryption and decryption in [CBC][], [CFB][], [OFB][],
[CTR][], and [GCM][] modes. See [CIPHER](#cipher) for examples.

<a name="des" />

### DES

Provides [3DES][] and [DES][] encryption and decryption in [ECB][] and
[CBC][] modes. See [CIPHER](#cipher) for examples.

<a name="rc2" />

### RC2

__Examples__

```js
// generate a random key and IV
var key = forge.random.getBytesSync(16);
var iv = forge.random.getBytesSync(8);

// encrypt some bytes
var cipher = forge.rc2.createEncryptionCipher(key);
cipher.start(iv);
cipher.update(forge.util.createBuffer(someBytes));
cipher.finish();
var encrypted = cipher.output;
// outputs encrypted hex
console.log(encrypted.toHex());

// decrypt some bytes
var cipher = forge.rc2.createDecryptionCipher(key);
cipher.start(iv);
cipher.update(encrypted);
cipher.finish();
// outputs decrypted hex
console.log(cipher.output.toHex());
```

PKI
---

Provides [X.509][] certificate support, ED25519 key generation and
signing/verifying, and RSA public and private key encoding, decoding,
encryption/decryption, and signing/verifying.

<a name="ed25519" />

### ED25519

Special thanks to [TweetNaCl.js][] for providing the bulk of the implementation.

__Examples__

```js
var ed25519 = forge.pki.ed25519;

// generate a random ED25519 keypair
var keypair = ed25519.generateKeyPair();
// `keypair.publicKey` is a node.js Buffer or Uint8Array
// `keypair.privateKey` is a node.js Buffer or Uint8Array

// generate a random ED25519 keypair based on a random 32-byte seed
var seed = forge.random.getBytesSync(32);
var keypair = ed25519.generateKeyPair({seed: seed});

// generate a random ED25519 keypair based on a "password" 32-byte seed
var password = 'Mai9ohgh6ahxee0jutheew0pungoozil';
var seed = new forge.util.ByteBuffer(password, 'utf8');
var keypair = ed25519.generateKeyPair({seed: seed});

// sign a UTF-8 message
var signature = ED25519.sign({
  message: 'test',
  // also accepts `binary` if you want to pass a binary string
  encoding: 'utf8',
  // node.js Buffer, Uint8Array, forge ByteBuffer, binary string
  privateKey: privateKey
});
// `signature` is a node.js Buffer or Uint8Array

// sign a message passed as a buffer
var signature = ED25519.sign({
  // also accepts a forge ByteBuffer or Uint8Array
  message: Buffer.from('test', 'utf8'),
  privateKey: privateKey
});

// sign a message digest (shorter "message" == better performance)
var md = forge.md.sha256.create();
md.update('test', 'utf8');
var signature = ED25519.sign({
  md: md,
  privateKey: privateKey
});

// verify a signature on a UTF-8 message
var verified = ED25519.verify({
  message: 'test',
  encoding: 'utf8',
  // node.js Buffer, Uint8Array, forge ByteBuffer, or binary string
  signature: signature,
  // node.js Buffer, Uint8Array, forge ByteBuffer, or binary string
  publicKey: publicKey
});
// `verified` is true/false

// sign a message passed as a buffer
var verified = ED25519.verify({
  // also accepts a forge ByteBuffer or Uint8Array
  message: Buffer.from('test', 'utf8'),
  // node.js Buffer, Uint8Array, forge ByteBuffer, or binary string
  signature: signature,
  // node.js Buffer, Uint8Array, forge ByteBuffer, or binary string
  publicKey: publicKey
});

// verify a signature on a message digest
var md = forge.md.sha256.create();
md.update('test', 'utf8');
var verified = ED25519.verify({
  md: md,
  // node.js Buffer, Uint8Array, forge ByteBuffer, or binary string
  signature: signature,
  // node.js Buffer, Uint8Array, forge ByteBuffer, or binary string
  publicKey: publicKey
});
```

<a name="rsa" />

### RSA

__Examples__

```js
var rsa = forge.pki.rsa;

// generate an RSA key pair synchronously
// *NOT RECOMMENDED*: Can be significantly slower than async and may block
// JavaScript execution. Will use native Node.js 10.12.0+ API if possible.
var keypair = rsa.generateKeyPair({bits: 2048, e: 0x10001});

// generate an RSA key pair asynchronously (uses web workers if available)
// use workers: -1 to run a fast core estimator to optimize # of workers
// *RECOMMENDED*: Can be significantly faster than sync. Will use native
// Node.js 10.12.0+ or WebCrypto API if possible.
rsa.generateKeyPair({bits: 2048, workers: 2}, function(err, keypair) {
  // keypair.privateKey, keypair.publicKey
});

// generate an RSA key pair in steps that attempt to run for a specified period
// of time on the main JS thread
var state = rsa.createKeyPairGenerationState(2048, 0x10001);
var step = function() {
  // run for 100 ms
  if(!rsa.stepKeyPairGenerationState(state, 100)) {
    setTimeout(step, 1);
  }
  else {
    // done, turn off progress indicator, use state.keys
  }
};
// turn on progress indicator, schedule generation to run
setTimeout(step);

// sign data with a private key and output DigestInfo DER-encoded bytes
// (defaults to RSASSA PKCS#1 v1.5)
var md = forge.md.sha1.create();
md.update('sign this', 'utf8');
var signature = privateKey.sign(md);

// verify data with a public key
// (defaults to RSASSA PKCS#1 v1.5)
var verified = publicKey.verify(md.digest().bytes(), signature);

// sign data using RSASSA-PSS where PSS uses a SHA-1 hash, a SHA-1 based
// masking function MGF1, and a 20 byte salt
var md = forge.md.sha1.create();
md.update('sign this', 'utf8');
var pss = forge.pss.create({
  md: forge.md.sha1.create(),
  mgf: forge.mgf.mgf1.create(forge.md.sha1.create()),
  saltLength: 20
  // optionally pass 'prng' with a custom PRNG implementation
  // optionalls pass 'salt' with a forge.util.ByteBuffer w/custom salt
});
var signature = privateKey.sign(md, pss);

// verify RSASSA-PSS signature
var pss = forge.pss.create({
  md: forge.md.sha1.create(),
  mgf: forge.mgf.mgf1.create(forge.md.sha1.create()),
  saltLength: 20
  // optionally pass 'prng' with a custom PRNG implementation
});
var md = forge.md.sha1.create();
md.update('sign this', 'utf8');
publicKey.verify(md.digest().getBytes(), signature, pss);

// encrypt data with a public key (defaults to RSAES PKCS#1 v1.5)
var encrypted = publicKey.encrypt(bytes);

// decrypt data with a private key (defaults to RSAES PKCS#1 v1.5)
var decrypted = privateKey.decrypt(encrypted);

// encrypt data with a public key using RSAES PKCS#1 v1.5
var encrypted = publicKey.encrypt(bytes, 'RSAES-PKCS1-V1_5');

// decrypt data with a private key using RSAES PKCS#1 v1.5
var decrypted = privateKey.decrypt(encrypted, 'RSAES-PKCS1-V1_5');

// encrypt data with a public key using RSAES-OAEP
var encrypted = publicKey.encrypt(bytes, 'RSA-OAEP');

// decrypt data with a private key using RSAES-OAEP
var decrypted = privateKey.decrypt(encrypted, 'RSA-OAEP');

// encrypt data with a public key using RSAES-OAEP/SHA-256
var encrypted = publicKey.encrypt(bytes, 'RSA-OAEP', {
  md: forge.md.sha256.create()
});

// decrypt data with a private key using RSAES-OAEP/SHA-256
var decrypted = privateKey.decrypt(encrypted, 'RSA-OAEP', {
  md: forge.md.sha256.create()
});

// encrypt data with a public key using RSAES-OAEP/SHA-256/MGF1-SHA-1
// compatible with Java's RSA/ECB/OAEPWithSHA-256AndMGF1Padding
var encrypted = publicKey.encrypt(bytes, 'RSA-OAEP', {
  md: forge.md.sha256.create(),
  mgf1: {
    md: forge.md.sha1.create()
  }
});

// decrypt data with a private key using RSAES-OAEP/SHA-256/MGF1-SHA-1
// compatible with Java's RSA/ECB/OAEPWithSHA-256AndMGF1Padding
var decrypted = privateKey.decrypt(encrypted, 'RSA-OAEP', {
  md: forge.md.sha256.create(),
  mgf1: {
    md: forge.md.sha1.create()
  }
});

```

<a name="rsakem" />

### RSA-KEM

__Examples__

```js
// generate an RSA key pair asynchronously (uses web workers if available)
// use workers: -1 to run a fast core estimator to optimize # of workers
forge.rsa.generateKeyPair({bits: 2048, workers: -1}, function(err, keypair) {
  // keypair.privateKey, keypair.publicKey
});

// generate and encapsulate a 16-byte secret key
var kdf1 = new forge.kem.kdf1(forge.md.sha1.create());
var kem = forge.kem.rsa.create(kdf1);
var result = kem.encrypt(keypair.publicKey, 16);
// result has 'encapsulation' and 'key'

// encrypt some bytes
var iv = forge.random.getBytesSync(12);
var someBytes = 'hello world!';
var cipher = forge.cipher.createCipher('AES-GCM', result.key);
cipher.start({iv: iv});
cipher.update(forge.util.createBuffer(someBytes));
cipher.finish();
var encrypted = cipher.output.getBytes();
var tag = cipher.mode.tag.getBytes();

// send 'encrypted', 'iv', 'tag', and result.encapsulation to recipient

// decrypt encapsulated 16-byte secret key
var kdf1 = new forge.kem.kdf1(forge.md.sha1.create());
var kem = forge.kem.rsa.create(kdf1);
var key = kem.decrypt(keypair.privateKey, result.encapsulation, 16);

// decrypt some bytes
var decipher = forge.cipher.createDecipher('AES-GCM', key);
decipher.start({iv: iv, tag: tag});
decipher.update(forge.util.createBuffer(encrypted));
var pass = decipher.finish();
// pass is false if there was a failure (eg: authentication tag didn't match)
if(pass) {
  // outputs 'hello world!'
  console.log(decipher.output.getBytes());
}

```

<a name="x509" />

### X.509

__Examples__

```js
var pki = forge.pki;

// convert a PEM-formatted public key to a Forge public key
var publicKey = pki.publicKeyFromPem(pem);

// convert a Forge public key to PEM-format
var pem = pki.publicKeyToPem(publicKey);

// convert an ASN.1 SubjectPublicKeyInfo to a Forge public key
var publicKey = pki.publicKeyFromAsn1(subjectPublicKeyInfo);

// convert a Forge public key to an ASN.1 SubjectPublicKeyInfo
var subjectPublicKeyInfo = pki.publicKeyToAsn1(publicKey);

// gets a SHA-1 RSAPublicKey fingerprint a byte buffer
pki.getPublicKeyFingerprint(key);

// gets a SHA-1 SubjectPublicKeyInfo fingerprint a byte buffer
pki.getPublicKeyFingerprint(key, {type: 'SubjectPublicKeyInfo'});

// gets a hex-encoded, colon-delimited SHA-1 RSAPublicKey public key fingerprint
pki.getPublicKeyFingerprint(key, {encoding: 'hex', delimiter: ':'});

// gets a hex-encoded, colon-delimited SHA-1 SubjectPublicKeyInfo public key fingerprint
pki.getPublicKeyFingerprint(key, {
  type: 'SubjectPublicKeyInfo',
  encoding: 'hex',
  delimiter: ':'
});

// gets a hex-encoded, colon-delimited MD5 RSAPublicKey public key fingerprint
pki.getPublicKeyFingerprint(key, {
  md: forge.md.md5.create(),
  encoding: 'hex',
  delimiter: ':'
});

// creates a CA store
var caStore = pki.createCaStore([/* PEM-encoded cert */, ...]);

// add a certificate to the CA store
caStore.addCertificate(certObjectOrPemString);

// gets the issuer (its certificate) for the given certificate
var issuerCert = caStore.getIssuer(subjectCert);

// verifies a certificate chain against a CA store
pki.verifyCertificateChain(caStore, chain, customVerifyCallback);

// signs a certificate using the given private key
cert.sign(privateKey);

// signs a certificate using SHA-256 instead of SHA-1
cert.sign(privateKey, forge.md.sha256.create());

// verifies an issued certificate using the certificates public key
var verified = issuer.verify(issued);

// generate a keypair and create an X.509v3 certificate
var keys = pki.rsa.generateKeyPair(2048);
var cert = pki.createCertificate();
cert.publicKey = keys.publicKey;
// alternatively set public key from a csr
//cert.publicKey = csr.publicKey;
// NOTE: serialNumber is the hex encoded value of an ASN.1 INTEGER.
// Conforming CAs should ensure serialNumber is:
// - no more than 20 octets
// - non-negative (prefix a '00' if your value starts with a '1' bit)
cert.serialNumber = '01';
cert.validity.notBefore = new Date();
cert.validity.notAfter = new Date();
cert.validity.notAfter.setFullYear(cert.validity.notBefore.getFullYear() + 1);
var attrs = [{
  name: 'commonName',
  value: 'example.org'
}, {
  name: 'countryName',
  value: 'US'
}, {
  shortName: 'ST',
  value: 'Virginia'
}, {
  name: 'localityName',
  value: 'Blacksburg'
}, {
  name: 'organizationName',
  value: 'Test'
}, {
  shortName: 'OU',
  value: 'Test'
}];
cert.setSubject(attrs);
// alternatively set subject from a csr
//cert.setSubject(csr.subject.attributes);
cert.setIssuer(attrs);
cert.setExtensions([{
  name: 'basicConstraints',
  cA: true
}, {
  name: 'keyUsage',
  keyCertSign: true,
  digitalSignature: true,
  nonRepudiation: true,
  keyEncipherment: true,
  dataEncipherment: true
}, {
  name: 'extKeyUsage',
  serverAuth: true,
  clientAuth: true,
  codeSigning: true,
  emailProtection: true,
  timeStamping: true
}, {
  name: 'nsCertType',
  client: true,
  server: true,
  email: true,
  objsign: true,
  sslCA: true,
  emailCA: true,
  objCA: true
}, {
  name: 'subjectAltName',
  altNames: [{
    type: 6, // URI
    value: 'http://example.org/webid#me'
  }, {
    type: 7, // IP
    ip: '127.0.0.1'
  }]
}, {
  name: 'subjectKeyIdentifier'
}]);
/* alternatively set extensions from a csr
var extensions = csr.getAttribute({name: 'extensionRequest'}).extensions;
// optionally add more extensions
extensions.push.apply(extensions, [{
  name: 'basicConstraints',
  cA: true
}, {
  name: 'keyUsage',
  keyCertSign: true,
  digitalSignature: true,
  nonRepudiation: true,
  keyEncipherment: true,
  dataEncipherment: true
}]);
cert.setExtensions(extensions);
*/
// self-sign certificate
cert.sign(keys.privateKey);

// convert a Forge certificate to PEM
var pem = pki.certificateToPem(cert);

// convert a Forge certificate from PEM
var cert = pki.certificateFromPem(pem);

// convert an ASN.1 X.509x3 object to a Forge certificate
var cert = pki.certificateFromAsn1(obj);

// convert a Forge certificate to an ASN.1 X.509v3 object
var asn1Cert = pki.certificateToAsn1(cert);
```

<a name="pkcs5" />

### PKCS#5

Provides the password-based key-derivation function from [PKCS#5][].

__Examples__

```js
// generate a password-based 16-byte key
// note an optional message digest can be passed as the final parameter
var salt = forge.random.getBytesSync(128);
var derivedKey = forge.pkcs5.pbkdf2('password', salt, numIterations, 16);

// generate key asynchronously
// note an optional message digest can be passed before the callback
forge.pkcs5.pbkdf2('password', salt, numIterations, 16, function(err, derivedKey) {
  // do something w/derivedKey
});
```

<a name="pkcs7" />

### PKCS#7

Provides cryptographically protected messages from [PKCS#7][].

__Examples__

```js
// convert a message from PEM
var p7 = forge.pkcs7.messageFromPem(pem);
// look at p7.recipients

// find a recipient by the issuer of a certificate
var recipient = p7.findRecipient(cert);

// decrypt
p7.decrypt(p7.recipients[0], privateKey);

// create a p7 enveloped message
var p7 = forge.pkcs7.createEnvelopedData();

// add a recipient
var cert = forge.pki.certificateFromPem(certPem);
p7.addRecipient(cert);

// set content
p7.content = forge.util.createBuffer('Hello');

// encrypt
p7.encrypt();

// convert message to PEM
var pem = forge.pkcs7.messageToPem(p7);

// create a degenerate PKCS#7 certificate container
// (CRLs not currently supported, only certificates)
var p7 = forge.pkcs7.createSignedData();
p7.addCertificate(certOrCertPem1);
p7.addCertificate(certOrCertPem2);
var pem = forge.pkcs7.messageToPem(p7);

// create PKCS#7 signed data with authenticatedAttributes
// attributes include: PKCS#9 content-type, message-digest, and signing-time
var p7 = forge.pkcs7.createSignedData();
p7.content = forge.util.createBuffer('Some content to be signed.', 'utf8');
p7.addCertificate(certOrCertPem);
p7.addSigner({
  key: privateKeyAssociatedWithCert,
  certificate: certOrCertPem,
  digestAlgorithm: forge.pki.oids.sha256,
  authenticatedAttributes: [{
    type: forge.pki.oids.contentType,
    value: forge.pki.oids.data
  }, {
    type: forge.pki.oids.messageDigest
    // value will be auto-populated at signing time
  }, {
    type: forge.pki.oids.signingTime,
    // value can also be auto-populated at signing time
    value: new Date()
  }]
});
p7.sign();
var pem = forge.pkcs7.messageToPem(p7);

// PKCS#7 Sign in detached mode.
// Includes the signature and certificate without the signed data.
p7.sign({detached: true});

```

<a name="pkcs8" />

### PKCS#8

__Examples__

```js
var pki = forge.pki;

// convert a PEM-formatted private key to a Forge private key
var privateKey = pki.privateKeyFromPem(pem);

// convert a Forge private key to PEM-format
var pem = pki.privateKeyToPem(privateKey);

// convert an ASN.1 PrivateKeyInfo or RSAPrivateKey to a Forge private key
var privateKey = pki.privateKeyFromAsn1(rsaPrivateKey);

// convert a Forge private key to an ASN.1 RSAPrivateKey
var rsaPrivateKey = pki.privateKeyToAsn1(privateKey);

// wrap an RSAPrivateKey ASN.1 object in a PKCS#8 ASN.1 PrivateKeyInfo
var privateKeyInfo = pki.wrapRsaPrivateKey(rsaPrivateKey);

// convert a PKCS#8 ASN.1 PrivateKeyInfo to PEM
var pem = pki.privateKeyInfoToPem(privateKeyInfo);

// encrypts a PrivateKeyInfo using a custom password and
// outputs an EncryptedPrivateKeyInfo
var encryptedPrivateKeyInfo = pki.encryptPrivateKeyInfo(
  privateKeyInfo, 'myCustomPasswordHere', {
    algorithm: 'aes256', // 'aes128', 'aes192', 'aes256', '3des'
  });

// decrypts an ASN.1 EncryptedPrivateKeyInfo that was encrypted
// with a custom password
var privateKeyInfo = pki.decryptPrivateKeyInfo(
  encryptedPrivateKeyInfo, 'myCustomPasswordHere');

// converts an EncryptedPrivateKeyInfo to PEM
var pem = pki.encryptedPrivateKeyToPem(encryptedPrivateKeyInfo);

// converts a PEM-encoded EncryptedPrivateKeyInfo to ASN.1 format
var encryptedPrivateKeyInfo = pki.encryptedPrivateKeyFromPem(pem);

// wraps and encrypts a Forge private key and outputs it in PEM format
var pem = pki.encryptRsaPrivateKey(privateKey, 'password');

// encrypts a Forge private key and outputs it in PEM format using OpenSSL's
// proprietary legacy format + encapsulated PEM headers (DEK-Info)
var pem = pki.encryptRsaPrivateKey(privateKey, 'password', {legacy: true});

// decrypts a PEM-formatted, encrypted private key
var privateKey = pki.decryptRsaPrivateKey(pem, 'password');

// sets an RSA public key from a private key
var publicKey = pki.setRsaPublicKey(privateKey.n, privateKey.e);
```

<a name="pkcs10" />

### PKCS#10

Provides certification requests or certificate signing requests (CSR) from
[PKCS#10][].

__Examples__

```js
// generate a key pair
var keys = forge.pki.rsa.generateKeyPair(2048);

// create a certification request (CSR)
var csr = forge.pki.createCertificationRequest();
csr.publicKey = keys.publicKey;
csr.setSubject([{
  name: 'commonName',
  value: 'example.org'
}, {
  name: 'countryName',
  value: 'US'
}, {
  shortName: 'ST',
  value: 'Virginia'
}, {
  name: 'localityName',
  value: 'Blacksburg'
}, {
  name: 'organizationName',
  value: 'Test'
}, {
  shortName: 'OU',
  value: 'Test'
}]);
// set (optional) attributes
csr.setAttributes([{
  name: 'challengePassword',
  value: 'password'
}, {
  name: 'unstructuredName',
  value: 'My Company, Inc.'
}, {
  name: 'extensionRequest',
  extensions: [{
    name: 'subjectAltName',
    altNames: [{
      // 2 is DNS type
      type: 2,
      value: 'test.domain.com'
    }, {
      type: 2,
      value: 'other.domain.com',
    }, {
      type: 2,
      value: 'www.domain.net'
    }]
  }]
}]);

// sign certification request
csr.sign(keys.privateKey);

// verify certification request
var verified = csr.verify();

// convert certification request to PEM-format
var pem = forge.pki.certificationRequestToPem(csr);

// convert a Forge certification request from PEM-format
var csr = forge.pki.certificationRequestFromPem(pem);

// get an attribute
csr.getAttribute({name: 'challengePassword'});

// get extensions array
csr.getAttribute({name: 'extensionRequest'}).extensions;

```

<a name="pkcs12" />

### PKCS#12

Provides the cryptographic archive file format from [PKCS#12][].

**Note for Chrome/Firefox/iOS/similar users**: If you have trouble importing
a PKCS#12 container, try using the TripleDES algorithm. It can be passed
to `forge.pkcs12.toPkcs12Asn1` using the `{algorithm: '3des'}` option.

__Examples__

```js
// decode p12 from base64
var p12Der = forge.util.decode64(p12b64);
// get p12 as ASN.1 object
var p12Asn1 = forge.asn1.fromDer(p12Der);
// decrypt p12 using the password 'password'
var p12 = forge.pkcs12.pkcs12FromAsn1(p12Asn1, 'password');
// decrypt p12 using non-strict parsing mode (resolves some ASN.1 parse errors)
var p12 = forge.pkcs12.pkcs12FromAsn1(p12Asn1, false, 'password');
// decrypt p12 using literally no password (eg: Mac OS X/apple push)
var p12 = forge.pkcs12.pkcs12FromAsn1(p12Asn1);
// decrypt p12 using an "empty" password (eg: OpenSSL with no password input)
var p12 = forge.pkcs12.pkcs12FromAsn1(p12Asn1, '');
// p12.safeContents is an array of safe contents, each of
// which contains an array of safeBags

// get bags by friendlyName
var bags = p12.getBags({friendlyName: 'test'});
// bags are key'd by attribute type (here "friendlyName")
// and the key values are an array of matching objects
var cert = bags.friendlyName[0];

// get bags by localKeyId
var bags = p12.getBags({localKeyId: buffer});
// bags are key'd by attribute type (here "localKeyId")
// and the key values are an array of matching objects
var cert = bags.localKeyId[0];

// get bags by localKeyId (input in hex)
var bags = p12.getBags({localKeyIdHex: '7b59377ff142d0be4565e9ac3d396c01401cd879'});
// bags are key'd by attribute type (here "localKeyId", *not* "localKeyIdHex")
// and the key values are an array of matching objects
var cert = bags.localKeyId[0];

// get bags by type
var bags = p12.getBags({bagType: forge.pki.oids.certBag});
// bags are key'd by bagType and each bagType key's value
// is an array of matches (in this case, certificate objects)
var cert = bags[forge.pki.oids.certBag][0];

// get bags by friendlyName and filter on bag type
var bags = p12.getBags({
  friendlyName: 'test',
  bagType: forge.pki.oids.certBag
});

// get key bags
var bags = p12.getBags({bagType: forge.pki.oids.keyBag});
// get key
var bag = bags[forge.pki.oids.keyBag][0];
var key = bag.key;
// if the key is in a format unrecognized by forge then
// bag.key will be `null`, use bag.asn1 to get the ASN.1
// representation of the key
if(bag.key === null) {
  var keyAsn1 = bag.asn1;
  // can now convert back to DER/PEM/etc for export
}

// generate a p12 using AES (default)
var p12Asn1 = forge.pkcs12.toPkcs12Asn1(
  privateKey, certificateChain, 'password');

// generate a p12 that can be imported by Chrome/Firefox/iOS
// (requires the use of Triple DES instead of AES)
var p12Asn1 = forge.pkcs12.toPkcs12Asn1(
  privateKey, certificateChain, 'password',
  {algorithm: '3des'});

// base64-encode p12
var p12Der = forge.asn1.toDer(p12Asn1).getBytes();
var p12b64 = forge.util.encode64(p12Der);

// create download link for p12
var a = document.createElement('a');
a.download = 'example.p12';
a.setAttribute('href', 'data:application/x-pkcs12;base64,' + p12b64);
a.appendChild(document.createTextNode('Download'));
```

<a name="asn" />

### ASN.1

Provides [ASN.1][] DER encoding and decoding.

__Examples__

```js
var asn1 = forge.asn1;

// create a SubjectPublicKeyInfo
var subjectPublicKeyInfo =
  asn1.create(asn1.Class.UNIVERSAL, asn1.Type.SEQUENCE, true, [
    // AlgorithmIdentifier
    asn1.create(asn1.Class.UNIVERSAL, asn1.Type.SEQUENCE, true, [
      // algorithm
      asn1.create(asn1.Class.UNIVERSAL, asn1.Type.OID, false,
        asn1.oidToDer(pki.oids['rsaEncryption']).getBytes()),
      // parameters (null)
      asn1.create(asn1.Class.UNIVERSAL, asn1.Type.NULL, false, '')
    ]),
    // subjectPublicKey
    asn1.create(asn1.Class.UNIVERSAL, asn1.Type.BITSTRING, false, [
      // RSAPublicKey
      asn1.create(asn1.Class.UNIVERSAL, asn1.Type.SEQUENCE, true, [
        // modulus (n)
        asn1.create(asn1.Class.UNIVERSAL, asn1.Type.INTEGER, false,
          _bnToBytes(key.n)),
        // publicExponent (e)
        asn1.create(asn1.Class.UNIVERSAL, asn1.Type.INTEGER, false,
          _bnToBytes(key.e))
      ])
    ])
  ]);

// serialize an ASN.1 object to DER format
var derBuffer = asn1.toDer(subjectPublicKeyInfo);

// deserialize to an ASN.1 object from a byte buffer filled with DER data
var object = asn1.fromDer(derBuffer);

// convert an OID dot-separated string to a byte buffer
var derOidBuffer = asn1.oidToDer('1.2.840.113549.1.1.5');

// convert a byte buffer with a DER-encoded OID to a dot-separated string
console.log(asn1.derToOid(derOidBuffer));
// output: 1.2.840.113549.1.1.5

// validates that an ASN.1 object matches a particular ASN.1 structure and
// captures data of interest from that structure for easy access
var publicKeyValidator = {
  name: 'SubjectPublicKeyInfo',
  tagClass: asn1.Class.UNIVERSAL,
  type: asn1.Type.SEQUENCE,
  constructed: true,
  captureAsn1: 'subjectPublicKeyInfo',
  value: [{
    name: 'SubjectPublicKeyInfo.AlgorithmIdentifier',
    tagClass: asn1.Class.UNIVERSAL,
    type: asn1.Type.SEQUENCE,
    constructed: true,
    value: [{
      name: 'AlgorithmIdentifier.algorithm',
      tagClass: asn1.Class.UNIVERSAL,
      type: asn1.Type.OID,
      constructed: false,
      capture: 'publicKeyOid'
    }]
  }, {
    // subjectPublicKey
    name: 'SubjectPublicKeyInfo.subjectPublicKey',
    tagClass: asn1.Class.UNIVERSAL,
    type: asn1.Type.BITSTRING,
    constructed: false,
    value: [{
      // RSAPublicKey
      name: 'SubjectPublicKeyInfo.subjectPublicKey.RSAPublicKey',
      tagClass: asn1.Class.UNIVERSAL,
      type: asn1.Type.SEQUENCE,
      constructed: true,
      optional: true,
      captureAsn1: 'rsaPublicKey'
    }]
  }]
};

var capture = {};
var errors = [];
if(!asn1.validate(
  publicKeyValidator, subjectPublicKeyInfo, validator, capture, errors)) {
  throw 'ASN.1 object is not a SubjectPublicKeyInfo.';
}
// capture.subjectPublicKeyInfo contains the full ASN.1 object
// capture.rsaPublicKey contains the full ASN.1 object for the RSA public key
// capture.publicKeyOid only contains the value for the OID
var oid = asn1.derToOid(capture.publicKeyOid);
if(oid !== pki.oids['rsaEncryption']) {
  throw 'Unsupported OID.';
}

// pretty print an ASN.1 object to a string for debugging purposes
asn1.prettyPrint(object);
```

Message Digests
----------------

<a name="sha1" />

### SHA1

Provides [SHA-1][] message digests.

__Examples__

```js
var md = forge.md.sha1.create();
md.update('The quick brown fox jumps over the lazy dog');
console.log(md.digest().toHex());
// output: 2fd4e1c67a2d28fced849ee1bb76e7391b93eb12
```

<a name="sha256" />

### SHA256

Provides [SHA-256][] message digests.

__Examples__

```js
var md = forge.md.sha256.create();
md.update('The quick brown fox jumps over the lazy dog');
console.log(md.digest().toHex());
// output: d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592
```

<a name="sha384" />

### SHA384

Provides [SHA-384][] message digests.

__Examples__

```js
var md = forge.md.sha384.create();
md.update('The quick brown fox jumps over the lazy dog');
console.log(md.digest().toHex());
// output: ca737f1014a48f4c0b6dd43cb177b0afd9e5169367544c494011e3317dbf9a509cb1e5dc1e85a941bbee3d7f2afbc9b1
```

<a name="sha512" />

### SHA512

Provides [SHA-512][] message digests.

__Examples__

```js
// SHA-512
var md = forge.md.sha512.create();
md.update('The quick brown fox jumps over the lazy dog');
console.log(md.digest().toHex());
// output: 07e547d9586f6a73f73fbac0435ed76951218fb7d0c8d788a309d785436bbb642e93a252a954f23912547d1e8a3b5ed6e1bfd7097821233fa0538f3db854fee6

// SHA-512/224
var md = forge.md.sha512.sha224.create();
md.update('The quick brown fox jumps over the lazy dog');
console.log(md.digest().toHex());
// output: 944cd2847fb54558d4775db0485a50003111c8e5daa63fe722c6aa37

// SHA-512/256
var md = forge.md.sha512.sha256.create();
md.update('The quick brown fox jumps over the lazy dog');
console.log(md.digest().toHex());
// output: dd9d67b371519c339ed8dbd25af90e976a1eeefd4ad3d889005e532fc5bef04d
```

<a name="md5" />

### MD5

Provides [MD5][] message digests.

__Examples__

```js
var md = forge.md.md5.create();
md.update('The quick brown fox jumps over the lazy dog');
console.log(md.digest().toHex());
// output: 9e107d9d372bb6826bd81d3542a419d6
```

<a name="hmac" />

### HMAC

Provides [HMAC][] w/any supported message digest algorithm.

__Examples__

```js
var hmac = forge.hmac.create();
hmac.start('sha1', 'Jefe');
hmac.update('what do ya want for nothing?');
console.log(hmac.digest().toHex());
// output: effcdf6ae5eb2fa2d27416d5f184df9c259a7c79
```

Utilities
---------

<a name="prime" />

### Prime

Provides an API for generating large, random, probable primes.

__Examples__

```js
// generate a random prime on the main JS thread
var bits = 1024;
forge.prime.generateProbablePrime(bits, function(err, num) {
  console.log('random prime', num.toString(16));
});

// generate a random prime using Web Workers (if available, otherwise
// falls back to the main thread)
var bits = 1024;
var options = {
  algorithm: {
    name: 'PRIMEINC',
    workers: -1 // auto-optimize # of workers
  }
};
forge.prime.generateProbablePrime(bits, options, function(err, num) {
  console.log('random prime', num.toString(16));
});
```

<a name="prng" />

### PRNG

Provides a [Fortuna][]-based cryptographically-secure pseudo-random number
generator, to be used with a cryptographic function backend, e.g. [AES][]. An
implementation using [AES][] as a backend is provided. An API for collecting
entropy is given, though if window.crypto.getRandomValues is available, it will
be used automatically.

__Examples__

```js
// get some random bytes synchronously
var bytes = forge.random.getBytesSync(32);
console.log(forge.util.bytesToHex(bytes));

// get some random bytes asynchronously
forge.random.getBytes(32, function(err, bytes) {
  console.log(forge.util.bytesToHex(bytes));
});

// collect some entropy if you'd like
forge.random.collect(someRandomBytes);
jQuery().mousemove(function(e) {
  forge.random.collectInt(e.clientX, 16);
  forge.random.collectInt(e.clientY, 16);
});

// specify a seed file for use with the synchronous API if you'd like
forge.random.seedFileSync = function(needed) {
  // get 'needed' number of random bytes from somewhere
  return fetchedRandomBytes;
};

// specify a seed file for use with the asynchronous API if you'd like
forge.random.seedFile = function(needed, callback) {
  // get the 'needed' number of random bytes from somewhere
  callback(null, fetchedRandomBytes);
});

// register the main thread to send entropy or a Web Worker to receive
// entropy on demand from the main thread
forge.random.registerWorker(self);

// generate a new instance of a PRNG with no collected entropy
var myPrng = forge.random.createInstance();
```

<a name="task" />

### Tasks

Provides queuing and synchronizing tasks in a web application.

__Examples__

```js
// TODO
```

<a name="util" />

### Utilities

Provides utility functions, including byte buffer support, base64,
bytes to/from hex, zlib inflate/deflate, etc.

__Examples__

```js
// encode/decode base64
var encoded = forge.util.encode64(str);
var str = forge.util.decode64(encoded);

// encode/decode UTF-8
var encoded = forge.util.encodeUtf8(str);
var str = forge.util.decodeUtf8(encoded);

// bytes to/from hex
var bytes = forge.util.hexToBytes(hex);
var hex = forge.util.bytesToHex(bytes);

// create an empty byte buffer
var buffer = forge.util.createBuffer();
// create a byte buffer from raw binary bytes
var buffer = forge.util.createBuffer(input, 'raw');
// create a byte buffer from utf8 bytes
var buffer = forge.util.createBuffer(input, 'utf8');

// get the length of the buffer in bytes
buffer.length();
// put bytes into the buffer
buffer.putBytes(bytes);
// put a 32-bit integer into the buffer
buffer.putInt32(10);
// buffer to hex
buffer.toHex();
// get a copy of the bytes in the buffer
bytes.bytes(/* count */);
// empty this buffer and get its contents
bytes.getBytes(/* count */);

// convert a forge buffer into a Node.js Buffer
// make sure you specify the encoding as 'binary'
var forgeBuffer = forge.util.createBuffer();
var nodeBuffer = Buffer.from(forgeBuffer.getBytes(), 'binary');

// convert a Node.js Buffer into a forge buffer
// make sure you specify the encoding as 'binary'
var nodeBuffer = Buffer.from('CAFE', 'hex');
var forgeBuffer = forge.util.createBuffer(nodeBuffer.toString('binary'));
```

<a name="log" />

### Logging

Provides logging to a javascript console using various categories and
levels of verbosity.

__Examples__

```js
// TODO
```

<a name="flash" />

### Flash Networking Support

The [flash README](./flash/README.md) provides details on rebuilding the
optional Flash component used for networking. It also provides details on
Policy Server support.

Security Considerations
-----------------------

When using this code please keep the following in mind:

- Cryptography is hard. Please review and test this code before depending on it
  for critical functionality.
- The nature of JavaScript is that execution of this code depends on trusting a
  very large set of JavaScript tools and systems. Consider runtime variations,
  runtime characteristics, runtime optimization, code optimization, code
  minimization, code obfuscation, bundling tools, possible bugs, the Forge code
  itself, and so on.
- If using pre-built bundles from [NPM][], another CDN, or similar, be aware
  someone else ran the tools to create those files.
- Use a secure transport channel such as [TLS][] to load scripts and consider
  using additional security mechanisms such as [Subresource Integrity][] script
  attributes.
- Use "native" functionality where possible. This can be critical when dealing
  with performance and random number generation. Note that the JavaScript
  random number algorithms should perform well if given suitable entropy.
- Understand possible attacks against cryptographic systems. For instance side
  channel and timing attacks may be possible due to the difficulty in
  implementing constant time algorithms in pure JavaScript.
- Certain features in this library are less susceptible to attacks depending on
  usage. This primarily includes features that deal with data format
  manipulation or those that are not involved in communication.

Library Background
------------------

* https://digitalbazaar.com/2010/07/20/javascript-tls-1/
* https://digitalbazaar.com/2010/07/20/javascript-tls-2/

Contact
-------

* Code: https://github.com/digitalbazaar/forge
* Bugs: https://github.com/digitalbazaar/forge/issues
* Email: support@digitalbazaar.com
* IRC: [#forgejs][] on [Libera.Chat][] (people may also be on [freenode][] for
  historical reasons).

Donations
---------

Financial support is welcome and helps contribute to futher development:

* For [PayPal][] please send to paypal@digitalbazaar.com.
* Something else? Please contact support@digitalbazaar.com.

[#forgejs]: https://webchat.freenode.net/?channels=#forgejs
[0.6.x]: https://github.com/digitalbazaar/forge/tree/0.6.x
[3DES]: https://en.wikipedia.org/wiki/Triple_DES
[AES]: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
[ASN.1]: https://en.wikipedia.org/wiki/ASN.1
[Browserify]: http://browserify.org/
[CBC]: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
[CFB]: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
[CTR]: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
[CommonJS]: https://en.wikipedia.org/wiki/CommonJS
[DES]: https://en.wikipedia.org/wiki/Data_Encryption_Standard
[ECB]: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
[Fortuna]: https://en.wikipedia.org/wiki/Fortuna_(PRNG)
[GCM]: https://en.wikipedia.org/wiki/GCM_mode
[HMAC]: https://en.wikipedia.org/wiki/HMAC
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[Karma]: https://karma-runner.github.io/
[Libera.Chat]: https://libera.chat/
[MD5]: https://en.wikipedia.org/wiki/MD5
[NPM]: https://www.npmjs.com/
[Node.js]: https://nodejs.org/
[OFB]: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
[PKCS#10]: https://en.wikipedia.org/wiki/Certificate_signing_request
[PKCS#12]: https://en.wikipedia.org/wiki/PKCS_%E2%99%AF12
[PKCS#5]: https://en.wikipedia.org/wiki/PKCS
[PKCS#7]: https://en.wikipedia.org/wiki/Cryptographic_Message_Syntax
[PayPal]: https://www.paypal.com/
[RC2]: https://en.wikipedia.org/wiki/RC2
[SHA-1]: https://en.wikipedia.org/wiki/SHA-1
[SHA-256]: https://en.wikipedia.org/wiki/SHA-256
[SHA-384]: https://en.wikipedia.org/wiki/SHA-384
[SHA-512]: https://en.wikipedia.org/wiki/SHA-512
[Subresource Integrity]: https://www.w3.org/TR/SRI/
[TLS]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[UMD]: https://github.com/umdjs/umd
[X.509]: https://en.wikipedia.org/wiki/X.509
[freenode]: https://freenode.net/
[unpkg]: https://unpkg.com/
[webpack]: https://webpack.github.io/
[TweetNaCl.js]: https://github.com/dchest/tweetnacl-js

## 3. optimization_CHANGELOG.md_20250924_204924.md

Forge ChangeLog
===============

## 1.3.1 - 2022-03-29

### Fixes
- RFC 3447 and RFC 8017 allow for optional `DigestAlgorithm` `NULL` parameters
  for `sha*` algorithms and require `NULL` paramters for `md2` and `md5`
  algorithms.

## 1.3.0 - 2022-03-17

### Security
- Three RSA PKCS#1 v1.5 signature verification issues were reported by Moosa
  Yahyazadeh (moosa-yahyazadeh@uiowa.edu).
- **HIGH**: Leniency in checking `digestAlgorithm` structure can lead to
  signature forgery.
  - The code is lenient in checking the digest algorithm structure. This can
    allow a crafted structure that steals padding bytes and uses unchecked
    portion of the PKCS#1 encoded message to forge a signature when a low
    public exponent is being used. For more information, please see
    ["Bleichenbacher's RSA signature forgery based on implementation
    error"](https://mailarchive.ietf.org/arch/msg/openpgp/5rnE9ZRN1AokBVj3VqblGlP63QE/)
    by Hal Finney.
  - CVE ID: [CVE-2022-24771](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-24771)
  - GHSA ID: [GHSA-cfm4-qjh2-4765](https://github.com/digitalbazaar/forge/security/advisories/GHSA-cfm4-qjh2-4765)
- **HIGH**: Failing to check tailing garbage bytes can lead to signature
  forgery.
  - The code does not check for tailing garbage bytes after decoding a
    `DigestInfo` ASN.1 structure. This can allow padding bytes to be removed
    and garbage data added to forge a signature when a low public exponent is
    being used.  For more information, please see ["Bleichenbacher's RSA
    signature forgery based on implementation
    error"](https://mailarchive.ietf.org/arch/msg/openpgp/5rnE9ZRN1AokBVj3VqblGlP63QE/)
    by Hal Finney.
  - CVE ID: [CVE-2022-24772](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-24772)
  - GHSA ID: [GHSA-x4jg-mjrx-434g](https://github.com/digitalbazaar/forge/security/advisories/GHSA-x4jg-mjrx-434g)
- **MEDIUM**: Leniency in checking type octet.
  - `DigestInfo` is not properly checked for proper ASN.1 structure. This can
    lead to successful verification with signatures that contain invalid
    structures but a valid digest.
  - CVE ID: [CVE-2022-24773](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-24773)
  - GHSA ID: [GHSA-2r2c-g63r-vccr](https://github.com/digitalbazaar/forge/security/advisories/GHSA-2r2c-g63r-vccr)

### Fixed
- [asn1] Add fallback to pretty print invalid UTF8 data.
- [asn1] `fromDer` is now more strict and will default to ensuring all input
  bytes are parsed or throw an error. A new option `parseAllBytes` can disable
  this behavior.
  - **NOTE**: The previous behavior is being changed since it can lead to
    security issues with crafted inputs. It is possible that code doing custom
    DER parsing may need to adapt to this new behavior and optional flag.
- [rsa] Add and use a validator to check for proper structure of parsed ASN.1
  `RSASSA-PKCS-v1_5` `DigestInfo` data. Additionally check that the hash
  algorithm identifier is a known value from RFC 8017
  `PKCS1-v1-5DigestAlgorithms`. An invalid `DigestInfo` or algorithm identifier
  will now throw an error.
  - **NOTE**: The previous lenient behavior is being changed to be more strict
    since it could lead to security issues with crafted inputs. It is possible
    that code may have to handle the errors from these stricter checks.

### Added
- [oid] Added missing RFC 8017 PKCS1-v1-5DigestAlgorithms algorithm
  identifiers:
  - `1.2.840.113549.2.2` / `md2`
  - `2.16.840.1.101.3.4.2.4` / `sha224`
  - `2.16.840.1.101.3.4.2.5` / `sha512-224`
  - `2.16.840.1.101.3.4.2.6` / `sha512-256`

## 1.2.1 - 2022-01-11

### Fixed
- [tests]: Load entire module to improve top-level testing and coverage
  reporting.
- [log]: Refactor logging setup to avoid use of `URLSearchParams`.

## 1.2.0 - 2022-01-07

### Fixed
- [x509] 'Expected' and 'Actual' issuers were backwards in verification failure
  message.

### Added
- [oid,x509]: Added OID `1.3.14.3.2.29 / sha1WithRSASignature` for sha1 with
  RSA. Considered a deprecated equivalent to `1.2.840.113549.1.1.5 /
  sha1WithRSAEncryption`. See [discussion and
  links](https://github.com/digitalbazaar/forge/issues/825).

### Changed
- [x509]: Reduce duplicate code. Add helper function to create a signature
  digest given an signature algorithm OID. Add helper function to verify
  signatures.

## 1.1.0 - 2022-01-06

### Fixed
- [x509]: Correctly compute certificate issuer and subject hashes to match
  behavior of openssl.
- [pem]: Accept certificate requests with "NEW" in the label. "BEGIN NEW
  CERTIFICATE REQUEST" handled as "BEGIN CERTIFICATE REQUEST".

## 1.0.0 - 2022-01-04

### Notes
- **1.0.0**!
- This project is over a decade old! Time for a 1.0.0 release.
- The URL related changes may expose bugs in some of the networking related
  code (unrelated to the much wider used cryptography code). The automated and
  manual test coverage for this code is weak at best. Issues or patches to
  update the code or tests would be appreciated.

### Removed
- **SECURITY**, **BREAKING**: Remove `forge.debug` API. The API has the
  potential for prototype pollution. This API was only briefly used by the
  maintainers for internal project debug purposes and was never intended to be
  used with untrusted user inputs. This API was not documented or advertised
  and is being removed rather than fixed.
- **SECURITY**, **BREAKING**: Remove `forge.util.parseUrl()` (and
  `forge.http.parseUrl` alias) and use the [WHATWG URL
  Standard](https://url.spec.whatwg.org/). `URL` is supported by modern browers
  and modern Node.js. This change is needed to address URL parsing security
  issues. If `forge.util.parseUrl()` is used directly or through `forge.xhr` or
  `forge.http` APIs, and support is needed for environments without `URL`
  support, then a polyfill must be used.
- **BREAKING**: Remove `forge.task` API. This API was never used, documented,
  or advertised by the maintainers. If anyone was using this API and wishes to
  continue development it in other project, please let the maintainers know.
  Due to use in the test suite, a modified version is located in
  `tests/support/`.
- **BREAKING**: Remove `forge.util.makeLink`, `forge.util.makeRequest`,
  `forge.util.parseFragment`, `forge.util.getQueryVariables`. Replace with
  `URL`, `URLSearchParams`, and custom code as needed.

### Changed
- **BREAKING**: Increase supported Node.js version to 6.13.0 for URL support.
- **BREAKING**: Renamed `master` branch to `main`.
- **BREAKING**: Release process updated to use tooling that prefixes versions
  with `v`. Other tools, scripts, or scanners may need to adapt.
- **BREAKING**: Remove docs related to Bower and
  [forge-dist](https://github.com/digitalbazaar/forge-dist). Install using
  [another method](./README.md#installation).

### Added
- OIDs for `surname`, `title`, and `givenName`.

### Fixed
- **BREAKING**: OID 2.5.4.5 name fixed from `serialName` to `serialNumber`.
  Depending on how applications used this id to name association it could cause
  compatibility issues.

## 0.10.0 - 2020-09-01

### Changed
- **BREAKING**: Node.js 4 no longer supported. The code *may* still work, and
  non-invasive patches to keep it working will be considered. However, more
  modern tools no longer support old Node.js versions making testing difficult.

### Removed
- **BREAKING**: Remove `util.getPath`, `util.setPath`, and `util.deletePath`.
  `util.setPath` had a potential prototype pollution security issue when used
  with unsafe inputs. These functions are not used by `forge` itself. They date
  from an early time when `forge` was targeted at providing general helper
  functions. The library direction changed to be more focused on cryptography.
  Many other excellent libraries are more suitable for general utilities. If
  you need a replacement for these functions, consider `get`, `set`, and `unset`
  from [lodash](https://lodash.com/). But also consider the potential similar
  security issues with those APIs.

## 0.9.2 - 2020-09-01

### Changed
- Added `util.setPath` security note to function docs and to README.

### Notes
- **SECURITY**: The `util.setPath` function has the potential to cause
  prototype pollution if used with unsafe input.
  - This function is **not** used internally by `forge`.
  - The rest of the library is unaffected by this issue.
  - **Do not** use unsafe input with this function.
  - Usage with known input should function as expected. (Including input
    intentionally using potentially problematic keys.)
  - No code changes will be made to address this issue in 0.9.x. The current
    behavior *could* be considered a feature rather than a security issue.
    0.10.0 will be released that removes `util.getPath` and `util.setPath`.
    Consider `get` and `set` from [lodash](https://lodash.com/) if you need
    replacements. But also consider the potential similar security issues with
    those APIs.
  - https://snyk.io/vuln/SNYK-JS-NODEFORGE-598677
  - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-7720

## 0.9.1 - 2019-09-26

### Fixed
- Ensure DES-CBC given IV is long enough for block size.

## 0.9.0 - 2019-09-04

### Added
- Add ed25519.publicKeyFromAsn1 and ed25519.privateKeyFromAsn1 APIs.
- A few OIDs used in EV certs.

### Fixed
- Improve ed25519 NativeBuffer check.

## 0.8.5 - 2019-06-18

### Fixed
- Remove use of `const`.

## 0.8.4 - 2019-05-22

### Changed
- Replace all instances of Node.js `new Buffer` with `Buffer.from` and `Buffer.alloc`.

## 0.8.3 - 2019-05-15

### Fixed
- Use basic character set for code.

## 0.8.2 - 2019-03-18

### Fixed
- Fix tag calculation when continuing an AES-GCM block.

### Changed
- Switch to eslint.

## 0.8.1 - 2019-02-23

### Fixed
- Fix off-by-1 bug with kem random generation.

## 0.8.0 - 2019-01-31

### Fixed
- Handle creation of certificates with `notBefore` and `notAfter` dates less
  than Jan 1, 1950 or greater than or equal to Jan 1, 2050.

### Added
- Add OID 2.5.4.13 "description".
- Add OID 2.16.840.1.113730.1.13 "nsComment".
  - Also handle extension when creating a certificate.
- `pki.verifyCertificateChain`:
  - Add `validityCheckDate` option to allow checking the certificate validity
    period against an arbitrary `Date` or `null` for no check at all. The
    current date is used by default.
- `tls.createConnection`:
  - Add `verifyOptions` option that passes through to
    `pki.verifyCertificateChain`. Can be used for the above `validityCheckDate`
    option.

### Changed
- Support WebCrypto API in web workers.
- `rsa.generateKeyPair`:
  - Use `crypto.generateKeyPair`/`crypto.generateKeyPairSync` on Node.js if
    available (10.12.0+) and not in pure JS mode.
  - Use JS fallback in `rsa.generateKeyPair` if `prng` option specified since
    this isn't supported by current native APIs.
  - Only run key generation comparison tests if keys will be deterministic.
- PhantomJS is deprecated, now using Headless Chrome with Karma.
- **Note**: Using Headless Chrome vs PhantomJS may cause newer JS features to
  slip into releases without proper support for older runtimes and browsers.
  Please report such issues and they will be addressed.
- `pki.verifyCertificateChain`:
  - Signature changed to `(caStore, chain, options)`. Older `(caStore, chain,
    verify)` signature is still supported. New style is to to pass in a
    `verify` option.

## 0.7.6 - 2018-08-14

### Added
- Test on Node.js 10.x.
- Support for PKCS#7 detached signatures.

### Changed
- Improve webpack/browser detection.

## 0.7.5 - 2018-03-30

### Fixed
- Remove use of `const`.

## 0.7.4 - 2018-03-07

### Fixed
- Potential regex denial of service in form.js.

### Added
- Support for ED25519.
- Support for baseN/base58.

## 0.7.3 - 2018-03-05

- Re-publish with npm 5.6.0 due to file timestamp issues.

## 0.7.2 - 2018-02-27

### Added
- Support verification of SHA-384 certificates.
- `1.2.840.10040.4.3'`/`dsa-with-sha1` OID.

### Fixed
- Support importing PKCS#7 data with no certificates. RFC 2315 sec 9.1 states
  certificates are optional.
- `asn1.equals` loop bug.
- Fortuna implementation bugs.

## 0.7.1 - 2017-03-27

### Fixed

- Fix digestLength for hashes based on SHA-512.

## 0.7.0 - 2017-02-07

### Fixed

- Fix test looping bugs so all tests are run.
- Improved ASN.1 parsing. Many failure cases eliminated. More sanity checks.
  Better behavior in default mode of parsing BIT STRINGs. Better handling of
  parsed BIT STRINGs in `toDer()`. More tests.
- Improve X.509 BIT STRING handling by using new capture modes.

### Changed

- Major refactor to use CommonJS plus a browser build system.
- Updated tests, examples, docs.
- Updated dependencies.
- Updated flash build system.
- Improve OID mapping code.
- Change test servers from Python to JavaScript.
- Improve PhantomJS support.
- Move Bower/bundle support to
  [forge-dist](https://github.com/digitalbazaar/forge-dist).
- **BREAKING**: Require minimal digest algorithm dependencies from individual
  modules.
- Enforce currently supported bit param values for byte buffer access. May be
  **BREAKING** for code that depended on unspecified and/or incorrect behavior.
- Improve `asn1.prettyPrint()` BIT STRING display.

### Added

- webpack bundler support via `npm run build`:
  - Builds `.js`, `.min.js`, and basic sourcemaps.
  - Basic build: `forge.js`.
  - Build with extra utils and networking support: `forge.all.js`.
  - Build WebWorker support: `prime.worker.js`.
- Browserify support in package.json.
- Karma browser testing.
- `forge.options` field.
- `forge.options.usePureJavaScript` flag.
- `forge.util.isNodejs` flag (used to select "native" APIs).
- Run PhantomJS tests in Travis-CI.
- Add "Donations" section to README.
- Add IRC to "Contact" section of README.
- Add "Security Considerations" section to README.
- Add pbkdf2 usePureJavaScript test.
- Add rsa.generateKeyPair async and usePureJavaScript tests.
- Add .editorconfig support.
- Add `md.all.js` which includes all digest algorithms.
- Add asn1 `equals()` and `copy()`.
- Add asn1 `validate()` capture options for BIT STRING contents and value.

### Removed

- **BREAKING**: Can no longer call `forge({...})` to create new instances.
- Remove a large amount of old cruft.

### Migration from 0.6.x to 0.7.x

- (all) If you used the feature to create a new forge instance with new
  configuration options you will need to rework your code. That ability has
  been removed due to implementation complexity. The main rare use was to set
  the option to use pure JavaScript. That is now available as a library global
  flag `forge.options.usePureJavaScript`.
- (npm,bower) If you used the default main file there is little to nothing to
  change.
- (npm) If you accessed a sub-resource like `forge/js/pki` you should either
  switch to just using the main `forge` and access `forge.pki` or update to
  `forge/lib/pki`.
- (bower) If you used a sub-resource like `forge/js/pki` you should switch to
  just using `forge` and access `forge.pki`. The bower release bundles
  everything in one minified file.
- (bower) A configured workerScript like
  `/bower_components/forge/js/prime.worker.js` will need to change to
  `/bower_components/forge/dist/prime.worker.min.js`.
- (all) If you used the networking support or flash socket support, you will
  need to use a custom build and/or adjust where files are loaded from. This
  functionality is not included in the bower distribution by default and is
  also now in a different directory.
- (all) The library should now directly support building custom bundles with
  webpack, browserify, or similar.
- (all) If building a custom bundle ensure the correct dependencies are
  included. In particular, note there is now a `md.all.js` file to include all
  digest algorithms. Individual files limit what they include by default to
  allow smaller custom builds. For instance, `pbdkf2.js` has a `sha1` default
  but does not include any algorithm files by default. This allows the
  possibility to include only `sha256` without the overhead of `sha1` and
  `sha512`.

### Notes

- This major update requires updating the version to 0.7.x. The existing
  work-in-progress "0.7.x" branch will be painfully rebased on top of this new
  0.7.x and moved forward to 0.8.x or later as needed.
- 0.7.x is a start of simplifying forge based on common issues and what has
  appeared to be the most common usage. Please file issues with feedback if the
  changes are problematic for your use cases.

## 0.6.x - 2016 and earlier

- See Git commit log or https://github.com/digitalbazaar/forge.

## 4. optimization_HISTORY.md_20250924_204923.md

2.7.0 / 2017-09-13
==================

  * feat: support fs.copyFile (#58)

2.6.0 / 2016-11-22
==================

  * Added fdatasync to fs api (#46)

2.5.0 / 2016-11-04
==================

  * feat: support fs.mkdtemp

2.4.0 / 2016-03-23
==================

  * add `fs.truncate()` [#34](https://github.com/normalize/mz/pull/34)

2.3.1 / 2016-02-01
==================

  * update `any-promise@v1`

2.3.0 / 2016-01-30
==================

  * feat(package): switch to `any-promise` to support more promise engines

2.2.0 / 2016-01-24
==================

  * feat(package): add index.js to files

2.1.0 / 2015-10-15
==================

 * support for readline library

2.0.0 / 2015-05-24
==================

 * support callbacks as well

1.2.0 / 2014-12-16
==================

 * refactor promisification to `thenify` and `thenify-all`

1.1.0 / 2014-11-14
==================

 * use `graceful-fs` if available

1.0.1 / 2014-08-18
==================

 * don't use `bluebird.promisify()` - unnecessarily wraps runtime errors, causing issues

1.0.0 / 2014-06-18
==================

 * use `bluebird` by default if found
 * support node 0.8

## 5. optimization_README.md_20250924_204921.md

# kind-of [![NPM version](https://img.shields.io/npm/v/kind-of.svg?style=flat)](https://www.npmjs.com/package/kind-of) [![NPM monthly downloads](https://img.shields.io/npm/dm/kind-of.svg?style=flat)](https://npmjs.org/package/kind-of) [![NPM total downloads](https://img.shields.io/npm/dt/kind-of.svg?style=flat)](https://npmjs.org/package/kind-of) [![Linux Build Status](https://img.shields.io/travis/jonschlinkert/kind-of.svg?style=flat&label=Travis)](https://travis-ci.org/jonschlinkert/kind-of)

> Get the native type of a value.

Please consider following this project's author, [Jon Schlinkert](https://github.com/jonschlinkert), and consider starring the project to show your :heart: and support.

## Install

Install with [npm](https://www.npmjs.com/):

```sh
$ npm install --save kind-of
```

Install with [bower](https://bower.io/)

```sh
$ bower install kind-of --save
```

## Why use this?

1. [it's fast](#benchmarks) | [optimizations](#optimizations)
2. [better type checking](#better-type-checking)

## Usage

> es5, es6, and browser ready

```js
var kindOf = require('kind-of');

kindOf(undefined);
//=> 'undefined'

kindOf(null);
//=> 'null'

kindOf(true);
//=> 'boolean'

kindOf(false);
//=> 'boolean'

kindOf(new Buffer(''));
//=> 'buffer'

kindOf(42);
//=> 'number'

kindOf('str');
//=> 'string'

kindOf(arguments);
//=> 'arguments'

kindOf({});
//=> 'object'

kindOf(Object.create(null));
//=> 'object'

kindOf(new Test());
//=> 'object'

kindOf(new Date());
//=> 'date'

kindOf([1, 2, 3]);
//=> 'array'

kindOf(/foo/);
//=> 'regexp'

kindOf(new RegExp('foo'));
//=> 'regexp'

kindOf(new Error('error'));
//=> 'error'

kindOf(function () {});
//=> 'function'

kindOf(function * () {});
//=> 'generatorfunction'

kindOf(Symbol('str'));
//=> 'symbol'

kindOf(new Map());
//=> 'map'

kindOf(new WeakMap());
//=> 'weakmap'

kindOf(new Set());
//=> 'set'

kindOf(new WeakSet());
//=> 'weakset'

kindOf(new Int8Array());
//=> 'int8array'

kindOf(new Uint8Array());
//=> 'uint8array'

kindOf(new Uint8ClampedArray());
//=> 'uint8clampedarray'

kindOf(new Int16Array());
//=> 'int16array'

kindOf(new Uint16Array());
//=> 'uint16array'

kindOf(new Int32Array());
//=> 'int32array'

kindOf(new Uint32Array());
//=> 'uint32array'

kindOf(new Float32Array());
//=> 'float32array'

kindOf(new Float64Array());
//=> 'float64array'
```

## Benchmarks

Benchmarked against [typeof](http://github.com/CodingFu/typeof) and [type-of](https://github.com/ForbesLindesay/type-of).

```bash
# arguments (32 bytes)
  kind-of x 17,024,098 ops/sec ±1.90% (86 runs sampled)
  lib-type-of x 11,926,235 ops/sec ±1.34% (83 runs sampled)
  lib-typeof x 9,245,257 ops/sec ±1.22% (87 runs sampled)

  fastest is kind-of (by 161% avg)

# array (22 bytes)
  kind-of x 17,196,492 ops/sec ±1.07% (88 runs sampled)
  lib-type-of x 8,838,283 ops/sec ±1.02% (87 runs sampled)
  lib-typeof x 8,677,848 ops/sec ±0.87% (87 runs sampled)

  fastest is kind-of (by 196% avg)

# boolean (24 bytes)
  kind-of x 16,841,600 ops/sec ±1.10% (86 runs sampled)
  lib-type-of x 8,096,787 ops/sec ±0.95% (87 runs sampled)
  lib-typeof x 8,423,345 ops/sec ±1.15% (86 runs sampled)

  fastest is kind-of (by 204% avg)

# buffer (38 bytes)
  kind-of x 14,848,060 ops/sec ±1.05% (86 runs sampled)
  lib-type-of x 3,671,577 ops/sec ±1.49% (87 runs sampled)
  lib-typeof x 8,360,236 ops/sec ±1.24% (86 runs sampled)

  fastest is kind-of (by 247% avg)

# date (30 bytes)
  kind-of x 16,067,761 ops/sec ±1.58% (86 runs sampled)
  lib-type-of x 8,954,436 ops/sec ±1.40% (87 runs sampled)
  lib-typeof x 8,488,307 ops/sec ±1.51% (84 runs sampled)

  fastest is kind-of (by 184% avg)

# error (36 bytes)
  kind-of x 9,634,090 ops/sec ±1.12% (89 runs sampled)
  lib-type-of x 7,735,624 ops/sec ±1.32% (86 runs sampled)
  lib-typeof x 7,442,160 ops/sec ±1.11% (90 runs sampled)

  fastest is kind-of (by 127% avg)

# function (34 bytes)
  kind-of x 10,031,494 ops/sec ±1.27% (86 runs sampled)
  lib-type-of x 9,502,757 ops/sec ±1.17% (89 runs sampled)
  lib-typeof x 8,278,985 ops/sec ±1.08% (88 runs sampled)

  fastest is kind-of (by 113% avg)

# null (24 bytes)
  kind-of x 18,159,808 ops/sec ±1.92% (86 runs sampled)
  lib-type-of x 12,927,635 ops/sec ±1.01% (88 runs sampled)
  lib-typeof x 7,958,234 ops/sec ±1.21% (89 runs sampled)

  fastest is kind-of (by 174% avg)

# number (22 bytes)
  kind-of x 17,846,779 ops/sec ±0.91% (85 runs sampled)
  lib-type-of x 3,316,636 ops/sec ±1.19% (86 runs sampled)
  lib-typeof x 2,329,477 ops/sec ±2.21% (85 runs sampled)

  fastest is kind-of (by 632% avg)

# object-plain (47 bytes)
  kind-of x 7,085,155 ops/sec ±1.05% (88 runs sampled)
  lib-type-of x 8,870,930 ops/sec ±1.06% (83 runs sampled)
  lib-typeof x 8,716,024 ops/sec ±1.05% (87 runs sampled)

  fastest is lib-type-of (by 112% avg)

# regex (25 bytes)
  kind-of x 14,196,052 ops/sec ±1.65% (84 runs sampled)
  lib-type-of x 9,554,164 ops/sec ±1.25% (88 runs sampled)
  lib-typeof x 8,359,691 ops/sec ±1.07% (87 runs sampled)

  fastest is kind-of (by 158% avg)

# string (33 bytes)
  kind-of x 16,131,428 ops/sec ±1.41% (85 runs sampled)
  lib-type-of x 7,273,172 ops/sec ±1.05% (87 runs sampled)
  lib-typeof x 7,382,635 ops/sec ±1.17% (85 runs sampled)

  fastest is kind-of (by 220% avg)

# symbol (34 bytes)
  kind-of x 17,011,537 ops/sec ±1.24% (86 runs sampled)
  lib-type-of x 3,492,454 ops/sec ±1.23% (89 runs sampled)
  lib-typeof x 7,471,235 ops/sec ±2.48% (87 runs sampled)

  fastest is kind-of (by 310% avg)

# template-strings (36 bytes)
  kind-of x 15,434,250 ops/sec ±1.46% (83 runs sampled)
  lib-type-of x 7,157,907 ops/sec ±0.97% (87 runs sampled)
  lib-typeof x 7,517,986 ops/sec ±0.92% (86 runs sampled)

  fastest is kind-of (by 210% avg)

# undefined (29 bytes)
  kind-of x 19,167,115 ops/sec ±1.71% (87 runs sampled)
  lib-type-of x 15,477,740 ops/sec ±1.63% (85 runs sampled)
  lib-typeof x 19,075,495 ops/sec ±1.17% (83 runs sampled)

  fastest is lib-typeof,kind-of

```

## Optimizations

In 7 out of 8 cases, this library is 2x-10x faster than other top libraries included in the benchmarks. There are a few things that lead to this performance advantage, none of them hard and fast rules, but all of them simple and repeatable in almost any code library:

1. Optimize around the fastest and most common use cases first. Of course, this will change from project-to-project, but I took some time to understand how and why `typeof` checks were being used in my own libraries and other libraries I use a lot.
2. Optimize around bottlenecks - In other words, the order in which conditionals are implemented is significant, because each check is only as fast as the failing checks that came before it. Here, the biggest bottleneck by far is checking for plain objects (an object that was created by the `Object` constructor). I opted to make this check happen by process of elimination rather than brute force up front (e.g. by using something like `val.constructor.name`), so that every other type check would not be penalized it.
3. Don't do uneccessary processing - why do `.slice(8, -1).toLowerCase();` just to get the word `regex`? It's much faster to do `if (type === '[object RegExp]') return 'regex'`
4. There is no reason to make the code in a microlib as terse as possible, just to win points for making it shorter. It's always better to favor performant code over terse code. You will always only be using a single `require()` statement to use the library anyway, regardless of how the code is written.

## Better type checking

kind-of seems to be more consistently "correct" than other type checking libs I've looked at. For example, here are some differing results from other popular libs:

### [typeof](https://github.com/CodingFu/typeof) lib

Incorrectly identifies instances of custom constructors (pretty common):

```js
var typeOf = require('typeof');
function Test() {}
console.log(typeOf(new Test()));
//=> 'test'
```

Returns `object` instead of `arguments`:

```js
function foo() {
  console.log(typeOf(arguments)) //=> 'object'
}
foo();
```

### [type-of](https://github.com/ForbesLindesay/type-of) lib

Incorrectly returns `object` for generator functions, buffers, `Map`, `Set`, `WeakMap` and `WeakSet`:

```js
function * foo() {}
console.log(typeOf(foo));
//=> 'object'
console.log(typeOf(new Buffer('')));
//=> 'object'
console.log(typeOf(new Map()));
//=> 'object'
console.log(typeOf(new Set()));
//=> 'object'
console.log(typeOf(new WeakMap()));
//=> 'object'
console.log(typeOf(new WeakSet()));
//=> 'object'
```

## About

<details>
<summary><strong>Contributing</strong></summary>

Pull requests and stars are always welcome. For bugs and feature requests, [please create an issue](../../issues/new).

</details>

<details>
<summary><strong>Running Tests</strong></summary>

Running and reviewing unit tests is a great way to get familiarized with a library and its API. You can install dependencies and run tests with the following command:

```sh
$ npm install && npm test
```

</details>

<details>
<summary><strong>Building docs</strong></summary>

_(This project's readme.md is generated by [verb](https://github.com/verbose/verb-generate-readme), please don't edit the readme directly. Any changes to the readme must be made in the [.verb.md](.verb.md) readme template.)_

To generate the readme, run the following command:

```sh
$ npm install -g verbose/verb#dev verb-generate-readme && verb
```

</details>

### Related projects

You might also be interested in these projects:

* [is-glob](https://www.npmjs.com/package/is-glob): Returns `true` if the given string looks like a glob pattern or an extglob pattern… [more](https://github.com/micromatch/is-glob) | [homepage](https://github.com/micromatch/is-glob "Returns `true` if the given string looks like a glob pattern or an extglob pattern. This makes it easy to create code that only uses external modules like node-glob when necessary, resulting in much faster code execution and initialization time, and a bet")
* [is-number](https://www.npmjs.com/package/is-number): Returns true if a number or string value is a finite number. Useful for regex… [more](https://github.com/jonschlinkert/is-number) | [homepage](https://github.com/jonschlinkert/is-number "Returns true if a number or string value is a finite number. Useful for regex matches, parsing, user input, etc.")
* [is-primitive](https://www.npmjs.com/package/is-primitive): Returns `true` if the value is a primitive.  | [homepage](https://github.com/jonschlinkert/is-primitive "Returns `true` if the value is a primitive. ")

### Contributors

| **Commits** | **Contributor** |  
| --- | --- |  
| 102 | [jonschlinkert](https://github.com/jonschlinkert) |  
| 3   | [aretecode](https://github.com/aretecode) |  
| 2   | [miguelmota](https://github.com/miguelmota) |  
| 1   | [doowb](https://github.com/doowb) |  
| 1   | [dtothefp](https://github.com/dtothefp) |  
| 1   | [ianstormtaylor](https://github.com/ianstormtaylor) |  
| 1   | [ksheedlo](https://github.com/ksheedlo) |  
| 1   | [pdehaan](https://github.com/pdehaan) |  
| 1   | [laggingreflex](https://github.com/laggingreflex) |  
| 1   | [tunnckoCore](https://github.com/tunnckoCore) |  
| 1   | [xiaofen9](https://github.com/xiaofen9) |  

### Author

**Jon Schlinkert**

* [GitHub Profile](https://github.com/jonschlinkert)
* [Twitter Profile](https://twitter.com/jonschlinkert)
* [LinkedIn Profile](https://linkedin.com/in/jonschlinkert)

### License

Copyright © 2020, [Jon Schlinkert](https://github.com/jonschlinkert).
Released under the [MIT License](LICENSE).

***

_This file was generated by [verb-generate-readme](https://github.com/verbose/verb-generate-readme), v0.8.0, on January 16, 2020._

## 6. optimization_CHANGELOG.md_20250924_204921.md

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v3.3.5](https://github.com/jsx-eslint/jsx-ast-utils/compare/v3.3.4...v3.3.5) - 2023-07-28

### Fixed

- [Fix] `extractProp`: support `JSXFragment` [`#132`](https://github.com/jsx-eslint/jsx-ast-utils/issues/132)

### Commits

- [Dev Deps] update `@babel/core`, `@babel/eslint-parser`, `@babel/parser`, `eslint` [`e5555d1`](https://github.com/jsx-eslint/jsx-ast-utils/commit/e5555d152dbe1e85324139756f637e65fe047976)
- [Tests] fix a test [`bde3ba9`](https://github.com/jsx-eslint/jsx-ast-utils/commit/bde3ba9c9dc294d5472eefa0b3f31ab0e1aed739)

## [v3.3.4](https://github.com/jsx-eslint/jsx-ast-utils/compare/v3.3.3...v3.3.4) - 2023-06-28

### Commits

- [Refactor] use `array.prototype.flat` `object.values` over `.reduce` [`bad51d0`](https://github.com/jsx-eslint/jsx-ast-utils/commit/bad51d062000ffdc19d925723a6515458318cf92)
- [meta] add `auto-changelog` [`af1de69`](https://github.com/jsx-eslint/jsx-ast-utils/commit/af1de693d1005144c13a75573631a670fa44547e)
- [Tests] add test for `import.meta` [`1d39f58`](https://github.com/jsx-eslint/jsx-ast-utils/commit/1d39f58c7bc6a89aa936e666b76e355c9436e854)
- [Dev Deps] update `@babel/core`, `@babel/eslint-parser`, `@babel/parser`, `aud`, `eslint`, `eslint-plugin-import` [`3baaf76`](https://github.com/jsx-eslint/jsx-ast-utils/commit/3baaf76c9c48ae85687ed23a3b9894c45927e081)
- [Fix] `TSNonNullExpression`: Handle function calls [`26cc3c4`](https://github.com/jsx-eslint/jsx-ast-utils/commit/26cc3c48165518b9fcdc9c625d918accc3e00107)
- [Dev Deps] update `eslint`, `@babel/core`, `@babel/parser`, `object.entries`, `object.fromentries` [`0e4f80c`](https://github.com/jsx-eslint/jsx-ast-utils/commit/0e4f80c2129c5b5ee50e4df2f25c5fb6728cbe8e)
- [Dev Deps] update `@babel/core`, `@babel/eslint-parser`, `@babel/parser`, `aud` [`b5427a6`](https://github.com/jsx-eslint/jsx-ast-utils/commit/b5427a65fac33e2264461b072b3edb078242dc85)
- [meta] run build in prepack, not prepublish [`a0f4f38`](https://github.com/jsx-eslint/jsx-ast-utils/commit/a0f4f383ddf82cd2914c7e594f356d9a78c80570)
- [Deps] update `array-includes` [`c479841`](https://github.com/jsx-eslint/jsx-ast-utils/commit/c479841d0b65188a3223541e885fa6286756a2c6)
- [Deps] update `object.assign` [`9685dce`](https://github.com/jsx-eslint/jsx-ast-utils/commit/9685dce823d71ac06fccd61d8aa8e13ba3d42f38)

<!-- auto-changelog-above -->

3.3.3 / 2022-08-08
==================
- [Fix] Mark ChainExpression as a noop (#109)
- [Deps] update `object.assign`
- [Dev Deps] update `@babel/core`, `@babel/eslint-parser`, `@babel/parser`, `eslint`

3.3.2 / 2022-07-06
==================
- [Fix] Handle `as` casts in TSNonNullExpression

3.3.1 / 2022-06-22
==================
- [Fix] `ArrayExpression`: handle sparse array (#117)
- [Deps] update `array-includes`
- [meta] move jest config to separate file
- [meta] use `npmignore` to autogenerate an npmignore file
- [Dev Deps] update `@babel/core`, `@babel/eslint-parser`, `@babel/parser`, `eslint`

3.3.0 / 2022-04-30
==================
- [New] add `JSXFragment`, `JSXText`; fix `JSXElement` to handle children
- [Dev Deps] update `@babel/core`, `@babel/parser`, `eslint`, `eslint-plugin-import`

3.2.2 / 2022-03-31
==================
- [Fix] `TSNonNullExpression`: handle computed MemberExpressions (#109)
- [Fix] avoid a crash in ChainExpressions in a TSAsExpression

3.2.1 / 2021-09-16
==================
- [patch] include project name in error logging (#113)
- [readme] update badges, URLs
- [Deps] update `array-includes`
- [meta] don‘t lint coverage results
- [meta] add GitHub org to FUNDING.yml
- [meta] add OpenCollective to FUNDING.yml
- [meta] run `aud` in `posttest`
- [meta] add Automatic Rebase and Require Allow Edits workflows
- [actions] use `node/install` instead of `node/run`; use `codecov` action
- [Tests] unpin `caniuse-lite`, since breaking change is fixed
- [Tests] pin `caniuse-lite`, due to breaking change in patch version
- [Tests] fix linting errors
- [Tests] migrate tests to Github Actions
- [Tests] stop using coveralls
- [Tests] skip failing fragment test in node 4
- [Dev Deps] update `@babel/core`, `@babel/parser`, `aud`, `eslint`, `eslint-plugin-import`, `object.entries`, `object.fromentries`

3.2.0 / 2020-12-16
==================
- [New] add support for fragment syntax (`<>`) (#108)
- [Fix] `TSNonNullExpression`: handle `ThisExpression`s (#108)
- [Deps] update `array-includes`, `object.assign`
- [Dev Deps] update `@babel/core`, `@babel/parser`, `eslint`, `eslint-config-airbnb-base`, `object.entries`, `object.fromentries`

3.1.0 / 2020-10-13
==================
- [New] add `TSNonNullExpression` (#105)
- [New] add `AssignmentExpression` (#106)
- [Dev Deps] update `eslint`

3.0.0 / 2020-10-06
==================
- [Breaking] Don't return node.start & node.end (#100)
- [Breaking] add `ChainExpression`; `CallExpression` now includes arguments (#102)
- [New] add `SequenceExpression` (#101)
- [Deps] update `object.assign`
- [Dev Deps] update `eslint`, `eslint-plugin-import`
- [Dev Deps] update `@babel/core`, `@babel/parser`, `eslint`, `eslint-plugin-import`
- [Tests] use proper `actual, expected` ordering for non-confusing failure messages

2.4.1 / 2020-06-11
==================
- [Fix] `expressions/TemplateLiteral`: use `.range[0]` instead of `.start`

2.4.0 / 2020-06-11
==================
- [New] Provide both range and start & end property on Node, support eslint v7 (#97)
- [Dev Deps] update `@babel/core`, `@babel/parser`, `eslint`, `eslint-config-airbnb-base`, `eslint-plugin-import`, `flow-parser`
- [meta] remove yarn registry from npmrc, so `npm publish` works

2.3.0 / 2020-05-24
==================
- [New] add nullish coalescing (#99)
- [New] add OptionalCallExpression (#99)
- [Deps] update `array-includes`
- [meta] add `safe-publish-latest`
- [Dev Deps] update `@babel/parser`, `babel-eslint`, `coveralls`, `eslint`, `eslint-config-airbnb-base`, `eslint-plugin-import`, `in-publish`, `object.entries`, `object.fromentries`, `rimraf`
- [Tests] on `node` `v14`; test all branches

2.2.3 / 2019-10-24
==================
- (fix) Fix crash on spread (#94)

2.2.2 / 2019-10-24
==================
- (improvement) Add support for retrieving props from a spread with object expression (#93)

2.2.1 / 2019-06-30
==================
- (improvement) Account for TypeCastExpression in the utils

2.2.0 / 2019-06-25
==================
- (fix) Fix getLiteralPropValue for TS-specific node types.
- (chore) upgrade dependencies.
- (improvement) Stop throwing errors when unknown AST nodes are encountered.
- (dev) CI changes.

2.1.0 / 2018-04-19
==================
- Fix undefined bug for template strings. #45
- Adding support for `objectRestSpread` within props #60
- Accommodate ExperimentalSpreadProperty in prop values #75
- Account for SpreadElement AST Nodes #76
- Support OptionalMemberExpression AST nodes #77
- Add support to Typescript's node types #72

2.0.1 / 2017-08-31
==================
- [fix] Add support for BindExpression


2.0.0 / 2017-07-07
==================
- [breaking] Remove undefined return from `propName` so it always returns a value.


1.4.1 / 2017-04-19
==================
- [fix] - Fixing fatal throw in `getPropValue` for `ArrowFunctionExpression`


1.4.0 / 2017-02-02
==================
- [new] Add eventHandlers and eventHandlersByType to API. These are the event names for DOM elements on JSX-using libraries such as React, inferno, and preact.


1.3.5 / 2016-12-14
==================
- [fix] Normalize literals "true" and "false" before converting to boolean in Literal prop value extractor.


1.3.4 / 2016-11-15
==================
- [fix] Recursively resolve JSXMemberExpression names for elementType. (i.e. `<Component.Render.Me />`). Fixes [#9](https://github.com/evcohen/jsx-ast-utils/issues/9)


1.3.3 / 2016-10-28
==================
- [fix] Add support for `ArrayExpression`.


1.3.2 / 2016-10-11
==================
- [fix] Add support for `UpdateExpression`.


1.3.1 / 2016-07-13
==================
- [fix] Add `JSXElement` to expression types to handle recursively extracting prop value.


1.3.0 / 2016-07-12
==================
- [new] Add support for `TaggedTemplateExpression`.


1.2.1 / 2016-06-15
==================
- [fix] Point to `lib` instead of `src` for root exports.


1.2.0 / 2016-06-15
==================
- [new] Export functions from root so they can be imported like the following: `require('jsx-ast-utils/{function}')`.


1.1.1 / 2016-06-12
==================
- [fix] Better support for expressions in `TemplateLiteral` extraction.


1.1.0 / 2016-06-10
==================
- [new] Support for namespaced element names.
- [new] Add `propName` to API to get correct name for prop.


1.0.1 / 2016-06-10
==================
- [fix] Return actual reserved words instead of string representations of them.


1.0.0 / 2016-06-09
==================
- Initial stable release

## 7. optimization_README.md_20250924_204920.md

# pretty-format

Stringify any JavaScript value.

- Serialize built-in JavaScript types.
- Serialize application-specific data types with built-in or user-defined plugins.

## Installation

```sh
$ yarn add pretty-format
```

## Usage

```js
const {format: prettyFormat} = require('pretty-format'); // CommonJS
```

```js
import {format as prettyFormat} from 'pretty-format'; // ES2015 modules
```

```js
const val = {object: {}};
val.circularReference = val;
val[Symbol('foo')] = 'foo';
val.map = new Map([['prop', 'value']]);
val.array = [-0, Infinity, NaN];

console.log(prettyFormat(val));
/*
Object {
  "array": Array [
    -0,
    Infinity,
    NaN,
  ],
  "circularReference": [Circular],
  "map": Map {
    "prop" => "value",
  },
  "object": Object {},
  Symbol(foo): "foo",
}
*/
```

## Usage with options

```js
function onClick() {}

console.log(prettyFormat(onClick));
/*
[Function onClick]
*/

const options = {
  printFunctionName: false,
};
console.log(prettyFormat(onClick, options));
/*
[Function]
*/
```

<!-- prettier-ignore -->
| key                   | type      | default    | description                                             |
| :-------------------- | :-------- | :--------- | :------------------------------------------------------ |
| `callToJSON`          | `boolean` | `true`     | call `toJSON` method (if it exists) on objects          |
| `compareKeys`         | `function`| `undefined`| compare function used when sorting object keys          |
| `escapeRegex`         | `boolean` | `false`    | escape special characters in regular expressions        |
| `escapeString`        | `boolean` | `true`     | escape special characters in strings                    |
| `highlight`           | `boolean` | `false`    | highlight syntax with colors in terminal (some plugins) |
| `indent`              | `number`  | `2`        | spaces in each level of indentation                     |
| `maxDepth`            | `number`  | `Infinity` | levels to print in arrays, objects, elements, and so on |
| `maxWidth`            | `number`  | `Infinity` | number of elements to print in arrays, sets, and so on  |
| `min`                 | `boolean` | `false`    | minimize added space: no indentation nor line breaks    |
| `plugins`             | `array`   | `[]`       | plugins to serialize application-specific data types    |
| `printBasicPrototype` | `boolean` | `false`    | print the prototype for plain objects and arrays        |
| `printFunctionName`   | `boolean` | `true`     | include or omit the name of a function                  |
| `theme`               | `object`  |            | colors to highlight syntax in terminal                  |

Property values of `theme` are from [ansi-styles colors](https://github.com/chalk/ansi-styles#colors)

```js
const DEFAULT_THEME = {
  comment: 'gray',
  content: 'reset',
  prop: 'yellow',
  tag: 'cyan',
  value: 'green',
};
```

## Usage with plugins

The `pretty-format` package provides some built-in plugins, including:

- `ReactElement` for elements from `react`
- `ReactTestComponent` for test objects from `react-test-renderer`

```js
// CommonJS
const React = require('react');
const renderer = require('react-test-renderer');
const {format: prettyFormat, plugins} = require('pretty-format');

const {ReactElement, ReactTestComponent} = plugins;
```

```js
// ES2015 modules and destructuring assignment
import React from 'react';
import renderer from 'react-test-renderer';
import {plugins, format as prettyFormat} from 'pretty-format';

const {ReactElement, ReactTestComponent} = plugins;
```

```js
const onClick = () => {};
const element = React.createElement('button', {onClick}, 'Hello World');

const formatted1 = prettyFormat(element, {
  plugins: [ReactElement],
  printFunctionName: false,
});
const formatted2 = prettyFormat(renderer.create(element).toJSON(), {
  plugins: [ReactTestComponent],
  printFunctionName: false,
});
/*
<button
  onClick=[Function]
>
  Hello World
</button>
*/
```

## Usage in Jest

For snapshot tests, Jest uses `pretty-format` with options that include some of its built-in plugins. For this purpose, plugins are also known as **snapshot serializers**.

To serialize application-specific data types, you can add modules to `devDependencies` of a project, and then:

In an **individual** test file, you can add a module as follows. It precedes any modules from Jest configuration.

```js
import serializer from 'my-serializer-module';
expect.addSnapshotSerializer(serializer);

// tests which have `expect(value).toMatchSnapshot()` assertions
```

For **all** test files, you can specify modules in Jest configuration. They precede built-in plugins for React, HTML, and Immutable.js data types. For example, in a `package.json` file:

```json
{
  "jest": {
    "snapshotSerializers": ["my-serializer-module"]
  }
}
```

## Writing plugins

A plugin is a JavaScript object.

If `options` has a `plugins` array: for the first plugin whose `test(val)` method returns a truthy value, then `prettyFormat(val, options)` returns the result from either:

- `serialize(val, …)` method of the **improved** interface (available in **version 21** or later)
- `print(val, …)` method of the **original** interface (if plugin does not have `serialize` method)

### test

Write `test` so it can receive `val` argument of any type. To serialize **objects** which have certain properties, then a guarded expression like `val != null && …` or more concise `val && …` prevents the following errors:

- `TypeError: Cannot read property 'whatever' of null`
- `TypeError: Cannot read property 'whatever' of undefined`

For example, `test` method of built-in `ReactElement` plugin:

```js
const elementSymbol = Symbol.for('react.element');
const test = val => val && val.$$typeof === elementSymbol;
```

Pay attention to efficiency in `test` because `pretty-format` calls it often.

### serialize

The **improved** interface is available in **version 21** or later.

Write `serialize` to return a string, given the arguments:

- `val` which “passed the test”
- unchanging `config` object: derived from `options`
- current `indentation` string: concatenate to `indent` from `config`
- current `depth` number: compare to `maxDepth` from `config`
- current `refs` array: find circular references in objects
- `printer` callback function: serialize children

### config

<!-- prettier-ignore -->
| key                 | type      | description                                             |
| :------------------ | :-------- | :------------------------------------------------------ |
| `callToJSON`        | `boolean` | call `toJSON` method (if it exists) on objects          |
| `compareKeys`       | `function`| compare function used when sorting object keys          |
| `colors`            | `Object`  | escape codes for colors to highlight syntax             |
| `escapeRegex`       | `boolean` | escape special characters in regular expressions        |
| `escapeString`      | `boolean` | escape special characters in strings                    |
| `indent`            | `string`  | spaces in each level of indentation                     |
| `maxDepth`          | `number`  | levels to print in arrays, objects, elements, and so on |
| `min`               | `boolean` | minimize added space: no indentation nor line breaks    |
| `plugins`           | `array`   | plugins to serialize application-specific data types    |
| `printFunctionName` | `boolean` | include or omit the name of a function                  |
| `spacingInner`      | `string`  | spacing to separate items in a list                     |
| `spacingOuter`      | `string`  | spacing to enclose a list of items                      |

Each property of `colors` in `config` corresponds to a property of `theme` in `options`:

- the key is the same (for example, `tag`)
- the value in `colors` is a object with `open` and `close` properties whose values are escape codes from [ansi-styles](https://github.com/chalk/ansi-styles) for the color value in `theme` (for example, `'cyan'`)

Some properties in `config` are derived from `min` in `options`:

- `spacingInner` and `spacingOuter` are **newline** if `min` is `false`
- `spacingInner` is **space** and `spacingOuter` is **empty string** if `min` is `true`

### Example of serialize and test

This plugin is a pattern you can apply to serialize composite data types. Side note: `pretty-format` does not need a plugin to serialize arrays.

```js
// We reused more code when we factored out a function for child items
// that is independent of depth, name, and enclosing punctuation (see below).
const SEPARATOR = ',';
function serializeItems(items, config, indentation, depth, refs, printer) {
  if (items.length === 0) {
    return '';
  }
  const indentationItems = indentation + config.indent;
  return (
    config.spacingOuter +
    items
      .map(
        item =>
          indentationItems +
          printer(item, config, indentationItems, depth, refs), // callback
      )
      .join(SEPARATOR + config.spacingInner) +
    (config.min ? '' : SEPARATOR) + // following the last item
    config.spacingOuter +
    indentation
  );
}

const plugin = {
  test(val) {
    return Array.isArray(val);
  },
  serialize(array, config, indentation, depth, refs, printer) {
    const name = array.constructor.name;
    return ++depth > config.maxDepth
      ? `[${name}]`
      : `${config.min ? '' : `${name} `}[${serializeItems(
          array,
          config,
          indentation,
          depth,
          refs,
          printer,
        )}]`;
  },
};
```

```js
const val = {
  filter: 'completed',
  items: [
    {
      text: 'Write test',
      completed: true,
    },
    {
      text: 'Write serialize',
      completed: true,
    },
  ],
};
```

```js
console.log(
  prettyFormat(val, {
    plugins: [plugin],
  }),
);
/*
Object {
  "filter": "completed",
  "items": Array [
    Object {
      "completed": true,
      "text": "Write test",
    },
    Object {
      "completed": true,
      "text": "Write serialize",
    },
  ],
}
*/
```

```js
console.log(
  prettyFormat(val, {
    indent: 4,
    plugins: [plugin],
  }),
);
/*
Object {
    "filter": "completed",
    "items": Array [
        Object {
            "completed": true,
            "text": "Write test",
        },
        Object {
            "completed": true,
            "text": "Write serialize",
        },
    ],
}
*/
```

```js
console.log(
  prettyFormat(val, {
    maxDepth: 1,
    plugins: [plugin],
  }),
);
/*
Object {
  "filter": "completed",
  "items": [Array],
}
*/
```

```js
console.log(
  prettyFormat(val, {
    min: true,
    plugins: [plugin],
  }),
);
/*
{"filter": "completed", "items": [{"completed": true, "text": "Write test"}, {"completed": true, "text": "Write serialize"}]}
*/
```

### print

The **original** interface is adequate for plugins:

- that **do not** depend on options other than `highlight` or `min`
- that **do not** depend on `depth` or `refs` in recursive traversal, and
- if values either
  - do **not** require indentation, or
  - do **not** occur as children of JavaScript data structures (for example, array)

Write `print` to return a string, given the arguments:

- `val` which “passed the test”
- current `printer(valChild)` callback function: serialize children
- current `indenter(lines)` callback function: indent lines at the next level
- unchanging `config` object: derived from `options`
- unchanging `colors` object: derived from `options`

The 3 properties of `config` are `min` in `options` and:

- `spacing` and `edgeSpacing` are **newline** if `min` is `false`
- `spacing` is **space** and `edgeSpacing` is **empty string** if `min` is `true`

Each property of `colors` corresponds to a property of `theme` in `options`:

- the key is the same (for example, `tag`)
- the value in `colors` is a object with `open` and `close` properties whose values are escape codes from [ansi-styles](https://github.com/chalk/ansi-styles) for the color value in `theme` (for example, `'cyan'`)

### Example of print and test

This plugin prints functions with the **number of named arguments** excluding rest argument.

```js
const plugin = {
  print(val) {
    return `[Function ${val.name || 'anonymous'} ${val.length}]`;
  },
  test(val) {
    return typeof val === 'function';
  },
};
```

```js
const val = {
  onClick(event) {},
  render() {},
};

prettyFormat(val, {
  plugins: [plugin],
});
/*
Object {
  "onClick": [Function onClick 1],
  "render": [Function render 0],
}
*/

prettyFormat(val);
/*
Object {
  "onClick": [Function onClick],
  "render": [Function render],
}
*/
```

This plugin **ignores** the `printFunctionName` option. That limitation of the original `print` interface is a reason to use the improved `serialize` interface, described above.

```js
prettyFormat(val, {
  plugins: [pluginOld],
  printFunctionName: false,
});
/*
Object {
  "onClick": [Function onClick 1],
  "render": [Function render 0],
}
*/

prettyFormat(val, {
  printFunctionName: false,
});
/*
Object {
  "onClick": [Function],
  "render": [Function],
}
*/
```

## 8. optimization_CHANGELOG.md_20250924_204919.md

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.0.4](https://github.com/inspect-js/is-weakset/compare/v2.0.3...v2.0.4) - 2024-12-16

### Commits

- [types] use shared config [`5fe9848`](https://github.com/inspect-js/is-weakset/commit/5fe98485c31c8269b90fe93b6f0d002259510786)
- [actions] split out node 10-20, and 20+ [`bd400b9`](https://github.com/inspect-js/is-weakset/commit/bd400b94a77eddeea29f940a2e18708f760deaab)
- [Dev Deps] update `@arethetypeswrong/cli`, `@ljharb/eslint-config`, `@types/object-inspect`, `auto-changelog`, `object-inspect`, `tape` [`8b290fc`](https://github.com/inspect-js/is-weakset/commit/8b290fc32cdd37e4464a2f3df192e71bf77a4636)
- [Refactor] use `call-bound` directly [`265971b`](https://github.com/inspect-js/is-weakset/commit/265971b6c1cf9d01b4c48b7182e13b4d46e4825a)
- [Dev Deps] update `@arethetypeswrong/cli`, `@ljharb/tsconfig`, `@types/tape` [`f39dc78`](https://github.com/inspect-js/is-weakset/commit/f39dc787ab85cd24f62013f1dd416e2f3bf2197a)
- [Dev Deps] update `@arethetypeswrong/cli`, `@types/get-intrinsic`, `object-inspect` [`ce6c6a9`](https://github.com/inspect-js/is-weakset/commit/ce6c6a936bbd40743021b6b96835d328dd924e1b)
- [Deps] update `call-bind`, `get-intrinsic` [`ebd5d82`](https://github.com/inspect-js/is-weakset/commit/ebd5d822ca3b8479ebebc99d8f268a7c2a264f8e)
- [Tests] replace `aud` with `npm audit` [`3eb16c8`](https://github.com/inspect-js/is-weakset/commit/3eb16c8b9e9b368f1e2a342867e10972e81b194b)
- [Dev Deps] update `@arethetypeswrong/cli` [`9fe99f3`](https://github.com/inspect-js/is-weakset/commit/9fe99f3ebc084129576e4f467df8eef834b2f25f)
- [Dev Deps] add missing peer dep [`a2fc30e`](https://github.com/inspect-js/is-weakset/commit/a2fc30ed83a6592c6ac56b425ebadc311dc96102)

## [v2.0.3](https://github.com/inspect-js/is-weakset/compare/v2.0.2...v2.0.3) - 2024-03-08

### Commits

- [meta] use `npmignore` to autogenerate an npmignore file [`e70d6aa`](https://github.com/inspect-js/is-weakset/commit/e70d6aa49d997930d3d88103090279ca1e480c7d)
- add types [`c9bbc35`](https://github.com/inspect-js/is-weakset/commit/c9bbc35f4d87cfa206281ddf6eb0e595f7994b7e)
- [readme] remove dead badges [`fb443f6`](https://github.com/inspect-js/is-weakset/commit/fb443f66e34a71a4d4ff41e09429f7479c9f4895)
- [actions] remove redundant finisher [`eb292cc`](https://github.com/inspect-js/is-weakset/commit/eb292cc1c056725c1a9c7d5861c3bca03734710e)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `aud`, `auto-changelog`, `es5-shim`, `object-inspect`, `tape` [`49d0c35`](https://github.com/inspect-js/is-weakset/commit/49d0c3583793fa2f097b66198a3a33dc2846c659)
- [Dev Deps] update `@ljharb/eslint-config`, `aud`, `es6-shim`, `npmignore`, `object-inspect`, `tape` [`6ec0a57`](https://github.com/inspect-js/is-weakset/commit/6ec0a5720c92ac3624283580d4af58a1b8846f43)
- [actions] update rebase action to use reusable workflow [`d996166`](https://github.com/inspect-js/is-weakset/commit/d9961664d6beb649e3ea8ee9b80309a0b60252fa)
- [Deps] update `call-bind`, `get-intrinsic` [`e207da3`](https://github.com/inspect-js/is-weakset/commit/e207da3865a658e83c1e9f453edfc5c52e63ccc3)
- [meta] add missing `engines.node` [`4d9dd14`](https://github.com/inspect-js/is-weakset/commit/4d9dd14f6919c969d7e6b8378d3aae2a7ea78a8f)
- [Deps] update `get-intrinsic` [`cf796dd`](https://github.com/inspect-js/is-weakset/commit/cf796dd7e71ea08abb81332f244ae3ffd34bffd5)
- [meta] add `sideEffects` flag [`c88a25d`](https://github.com/inspect-js/is-weakset/commit/c88a25df1f14630d937e730e75fd6b182356fc0b)

## [v2.0.2](https://github.com/inspect-js/is-weakset/compare/v2.0.1...v2.0.2) - 2021-12-12

### Commits

- [actions] reuse common workflows [`a8f7c7f`](https://github.com/inspect-js/is-weakset/commit/a8f7c7fa22088dabbadf82cd52cf962eca646c59)
- [Tests] migrate tests to Github Actions [`f38af72`](https://github.com/inspect-js/is-weakset/commit/f38af729300d425360caad1763e7f904dcd3e393)
- [Refactor] use `call-bind` and `get-intrinsic` to be more robust [`5102e7e`](https://github.com/inspect-js/is-weakset/commit/5102e7ef227f06da1bc8dcee2579af74f1e1a477)
- [meta] do not publish github action workflow files [`6ac6e8e`](https://github.com/inspect-js/is-weakset/commit/6ac6e8e5b15181e73d30f6d37e41955372b07792)
- [actions] use `node/install` instead of `node/run`; use `codecov` action [`304af52`](https://github.com/inspect-js/is-weakset/commit/304af52f4c40743b055e252d50c8e804cac4054f)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `aud`, `auto-changelog`, `es6-shim`, `object-inspect`, `tape` [`b82fb5f`](https://github.com/inspect-js/is-weakset/commit/b82fb5fafdeea05f93420e0966fe63785362649a)
- [Tests] run `nyc` on all tests; use `tape` runner [`89e2611`](https://github.com/inspect-js/is-weakset/commit/89e26115ab1aa58b37816d6b5e2aad62508bd79c)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `es5-shim`, `object-inspect`, `safe-publish-latest`, `tape` [`42b0bdc`](https://github.com/inspect-js/is-weakset/commit/42b0bdc5a8785ddb589ea16629c933ec01359ca8)
- [actions] update codecov uploader [`112697a`](https://github.com/inspect-js/is-weakset/commit/112697aaf3b6f2e22275575ce4b684059fa5dcaa)
- [actions] add "Allow Edits" workflow [`1af6ffe`](https://github.com/inspect-js/is-weakset/commit/1af6ffe2793a5784ac70048e50850f4d6e650de4)
- [readme] remove travis badge [`dff769b`](https://github.com/inspect-js/is-weakset/commit/dff769b367aa4886ab082dd6330cbc54d0dcf03f)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `aud`, `object-inspect`, `tape` [`4494ced`](https://github.com/inspect-js/is-weakset/commit/4494cedea891e3617768b30721e3b5ddee5c41e4)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `es5-shim`, `tape` [`a2c11c6`](https://github.com/inspect-js/is-weakset/commit/a2c11c6dcef990b7f6fabb26d58837a7fe4f3a3e)
- [Tests] add `core-js` tests [`cd619e9`](https://github.com/inspect-js/is-weakset/commit/cd619e95f64cc02cbec8f4b0b29a806f371eab9e)
- [readme] add actions and codecov badges [`d3cbefe`](https://github.com/inspect-js/is-weakset/commit/d3cbefeb526773a565eb4e501b2e7da7947b215d)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `tape` [`3d54035`](https://github.com/inspect-js/is-weakset/commit/3d54035e2ca66969f6cc779b85902ac3507d7297)
- [Dev Deps] update `auto-changelog`, `eslint` [`a80fb4a`](https://github.com/inspect-js/is-weakset/commit/a80fb4a7c1a90a2929d80f9b2a9adaa56c94d2d2)
- [actions] switch Automatic Rease workflow to `pull_request_target` event [`b3b8aee`](https://github.com/inspect-js/is-weakset/commit/b3b8aeeb3e133d88da897d42530aea4bcc729b23)
- [Dev Deps] update `es5-shim`, `tape` [`5ba5ca8`](https://github.com/inspect-js/is-weakset/commit/5ba5ca84a3d4bb4acacb9fd9265a21476d4f0457)
- [meta] use `prepublishOnly` script for npm 7+ [`b4f7636`](https://github.com/inspect-js/is-weakset/commit/b4f76366574ac4b4d854c330cbad33a8d9ff48ff)
- [Dev Deps] update `auto-changelog`; add `aud` [`2ccd594`](https://github.com/inspect-js/is-weakset/commit/2ccd5944c8fd161fa463620de268bd6f40ff0e59)
- [Fix] when `WeakSet` lacks a `has`, return false [`53a2cbc`](https://github.com/inspect-js/is-weakset/commit/53a2cbce11d2493b4ff82132f3d14e22c909b541)
- [Tests] only audit prod deps [`f74aaf5`](https://github.com/inspect-js/is-weakset/commit/f74aaf5746fc49d424742184025288d0d565639c)
- [meta] normalize line endings [`31f60a6`](https://github.com/inspect-js/is-weakset/commit/31f60a6a70e38851743e602e30bb0907cd3cc6ba)

## [v2.0.1](https://github.com/inspect-js/is-weakset/compare/v2.0.0...v2.0.1) - 2019-12-17

### Fixed

- [Refactor] avoid top-level return, because babel and webpack are broken [`#79`](https://github.com/inspect-js/node-deep-equal/issues/79) [`#78`](https://github.com/inspect-js/node-deep-equal/issues/78) [`#7`](https://github.com/es-shims/Promise.allSettled/issues/7) [`#12`](https://github.com/airbnb/js-shims/issues/12)

### Commits

- [actions] add automatic rebasing / merge commit blocking [`d85eb2c`](https://github.com/inspect-js/is-weakset/commit/d85eb2ca5fe1f1890a04c5504e4c23d68db68447)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config` [`790128b`](https://github.com/inspect-js/is-weakset/commit/790128b8e7c2abe39f70a5c25a303646f8555487)
- [Dev Deps] update `tape` [`e4bda71`](https://github.com/inspect-js/is-weakset/commit/e4bda71a8a6b1233285e91f54a05a08b75cdbd6e)

## [v2.0.0](https://github.com/inspect-js/is-weakset/compare/v1.0.1...v2.0.0) - 2019-11-12

### Commits

- Initial commit [`095ce1f`](https://github.com/inspect-js/is-weakset/commit/095ce1f56c52aa547b57dd326e9b5c2c8a7c2765)
- Tests [`2e8f26d`](https://github.com/inspect-js/is-weakset/commit/2e8f26d1b632fbfe4ded276d046e34276780671b)
- implementation [`acae1ef`](https://github.com/inspect-js/is-weakset/commit/acae1ef8d29a84ff0729135ac4acfe42f18c1328)
- readme [`344db89`](https://github.com/inspect-js/is-weakset/commit/344db8951568a3206847e7b00820622c2364e1ff)
- npm init [`e318679`](https://github.com/inspect-js/is-weakset/commit/e318679acc2c3c168a32fb648ddf3d54ff3e6d5e)
- [meta] add `funding` field; create `FUNDING.yml` [`a1e9277`](https://github.com/inspect-js/is-weakset/commit/a1e927798405e643e570a43d0ee30f5ae16d9d18)
- [meta] add `safe-publish-latest`, `auto-changelog` [`066a08c`](https://github.com/inspect-js/is-weakset/commit/066a08cd939ec1efe433af23688f8c73d3524b5c)
- [Tests] add `npm run lint` [`6af0730`](https://github.com/inspect-js/is-weakset/commit/6af07301fda27f1450184f31b941cf9fbefe261d)
- [Tests] use shared travis-ci configs [`a44f4ec`](https://github.com/inspect-js/is-weakset/commit/a44f4ec03d734274e351acef37698272f3e500c1)
- Only apps should have lockfiles [`11e4115`](https://github.com/inspect-js/is-weakset/commit/11e41153e46eb3ead4be9187770fe8cb47a21e12)
- [Tests] add `npx aud` in `posttest` [`53ceba1`](https://github.com/inspect-js/is-weakset/commit/53ceba16b0a98f968e40439f7bd2ffc98a406de8)

## [v1.0.1](https://github.com/inspect-js/is-weakset/compare/v1.0.0...v1.0.1) - 2015-06-03

### Commits

- Tweaks [`cb3a689`](https://github.com/inspect-js/is-weakset/commit/cb3a68985d734632423ffe81704500bd04e95934)
- Add `related` section to readme [`7c2766b`](https://github.com/inspect-js/is-weakset/commit/7c2766b3e1992b34d5ad933f2cf8901352aa4fcd)

## v1.0.0 - 2015-02-18

### Commits

- init [`579f442`](https://github.com/inspect-js/is-weakset/commit/579f442c42afa4e3880f9f62b3ccea79e0b6edd5)

## 9. optimization_README.md_20250924_204918.md

# is-number [![NPM version](https://img.shields.io/npm/v/is-number.svg?style=flat)](https://www.npmjs.com/package/is-number) [![NPM monthly downloads](https://img.shields.io/npm/dm/is-number.svg?style=flat)](https://npmjs.org/package/is-number) [![NPM total downloads](https://img.shields.io/npm/dt/is-number.svg?style=flat)](https://npmjs.org/package/is-number) [![Linux Build Status](https://img.shields.io/travis/jonschlinkert/is-number.svg?style=flat&label=Travis)](https://travis-ci.org/jonschlinkert/is-number)

> Returns true if the value is a finite number.

Please consider following this project's author, [Jon Schlinkert](https://github.com/jonschlinkert), and consider starring the project to show your :heart: and support.

## Install

Install with [npm](https://www.npmjs.com/):

```sh
$ npm install --save is-number
```

## Why is this needed?

In JavaScript, it's not always as straightforward as it should be to reliably check if a value is a number. It's common for devs to use `+`, `-`, or `Number()` to cast a string value to a number (for example, when values are returned from user input, regex matches, parsers, etc). But there are many non-intuitive edge cases that yield unexpected results:

```js
console.log(+[]); //=> 0
console.log(+''); //=> 0
console.log(+'   '); //=> 0
console.log(typeof NaN); //=> 'number'
```

This library offers a performant way to smooth out edge cases like these.

## Usage

```js
const isNumber = require('is-number');
```

See the [tests](./test.js) for more examples.

### true

```js
isNumber(5e3);               // true
isNumber(0xff);              // true
isNumber(-1.1);              // true
isNumber(0);                 // true
isNumber(1);                 // true
isNumber(1.1);               // true
isNumber(10);                // true
isNumber(10.10);             // true
isNumber(100);               // true
isNumber('-1.1');            // true
isNumber('0');               // true
isNumber('012');             // true
isNumber('0xff');            // true
isNumber('1');               // true
isNumber('1.1');             // true
isNumber('10');              // true
isNumber('10.10');           // true
isNumber('100');             // true
isNumber('5e3');             // true
isNumber(parseInt('012'));   // true
isNumber(parseFloat('012')); // true
```

### False

Everything else is false, as you would expect:

```js
isNumber(Infinity);          // false
isNumber(NaN);               // false
isNumber(null);              // false
isNumber(undefined);         // false
isNumber('');                // false
isNumber('   ');             // false
isNumber('foo');             // false
isNumber([1]);               // false
isNumber([]);                // false
isNumber(function () {});    // false
isNumber({});                // false
```

## Release history

### 7.0.0

* Refactor. Now uses `.isFinite` if it exists.
* Performance is about the same as v6.0 when the value is a string or number. But it's now 3x-4x faster when the value is not a string or number.

### 6.0.0

* Optimizations, thanks to @benaadams.

### 5.0.0

**Breaking changes**

* removed support for `instanceof Number` and `instanceof String`

## Benchmarks

As with all benchmarks, take these with a grain of salt. See the [benchmarks](./benchmark/index.js) for more detail.

```
# all
v7.0 x 413,222 ops/sec ±2.02% (86 runs sampled)
v6.0 x 111,061 ops/sec ±1.29% (85 runs sampled)
parseFloat x 317,596 ops/sec ±1.36% (86 runs sampled)
fastest is 'v7.0'

# string
v7.0 x 3,054,496 ops/sec ±1.05% (89 runs sampled)
v6.0 x 2,957,781 ops/sec ±0.98% (88 runs sampled)
parseFloat x 3,071,060 ops/sec ±1.13% (88 runs sampled)
fastest is 'parseFloat,v7.0'

# number
v7.0 x 3,146,895 ops/sec ±0.89% (89 runs sampled)
v6.0 x 3,214,038 ops/sec ±1.07% (89 runs sampled)
parseFloat x 3,077,588 ops/sec ±1.07% (87 runs sampled)
fastest is 'v6.0'
```

## About

<details>
<summary><strong>Contributing</strong></summary>

Pull requests and stars are always welcome. For bugs and feature requests, [please create an issue](../../issues/new).

</details>

<details>
<summary><strong>Running Tests</strong></summary>

Running and reviewing unit tests is a great way to get familiarized with a library and its API. You can install dependencies and run tests with the following command:

```sh
$ npm install && npm test
```

</details>

<details>
<summary><strong>Building docs</strong></summary>

_(This project's readme.md is generated by [verb](https://github.com/verbose/verb-generate-readme), please don't edit the readme directly. Any changes to the readme must be made in the [.verb.md](.verb.md) readme template.)_

To generate the readme, run the following command:

```sh
$ npm install -g verbose/verb#dev verb-generate-readme && verb
```

</details>

### Related projects

You might also be interested in these projects:

* [is-plain-object](https://www.npmjs.com/package/is-plain-object): Returns true if an object was created by the `Object` constructor. | [homepage](https://github.com/jonschlinkert/is-plain-object "Returns true if an object was created by the `Object` constructor.")
* [is-primitive](https://www.npmjs.com/package/is-primitive): Returns `true` if the value is a primitive.  | [homepage](https://github.com/jonschlinkert/is-primitive "Returns `true` if the value is a primitive. ")
* [isobject](https://www.npmjs.com/package/isobject): Returns true if the value is an object and not an array or null. | [homepage](https://github.com/jonschlinkert/isobject "Returns true if the value is an object and not an array or null.")
* [kind-of](https://www.npmjs.com/package/kind-of): Get the native type of a value. | [homepage](https://github.com/jonschlinkert/kind-of "Get the native type of a value.")

### Contributors

| **Commits** | **Contributor** | 
| --- | --- |
| 49 | [jonschlinkert](https://github.com/jonschlinkert) |
| 5 | [charlike-old](https://github.com/charlike-old) |
| 1 | [benaadams](https://github.com/benaadams) |
| 1 | [realityking](https://github.com/realityking) |

### Author

**Jon Schlinkert**

* [LinkedIn Profile](https://linkedin.com/in/jonschlinkert)
* [GitHub Profile](https://github.com/jonschlinkert)
* [Twitter Profile](https://twitter.com/jonschlinkert)

### License

Copyright © 2018, [Jon Schlinkert](https://github.com/jonschlinkert).
Released under the [MIT License](LICENSE).

***

_This file was generated by [verb-generate-readme](https://github.com/verbose/verb-generate-readme), v0.6.0, on June 15, 2018._

## 10. optimization_CHANGELOG.md_20250924_204918.md

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.0.3](https://github.com/inspect-js/is-map/compare/v2.0.2...v2.0.3) - 2024-03-08

### Commits

- [actions] reuse common workflows [`ce10d0f`](https://github.com/inspect-js/is-map/commit/ce10d0f82fcec150b5d283202c1988887d618895)
- [meta] use `npmignore` to autogenerate an npmignore file [`e07e23a`](https://github.com/inspect-js/is-map/commit/e07e23affca99f469937dade44abc02e05a26739)
- add types [`cd13cfb`](https://github.com/inspect-js/is-map/commit/cd13cfb54647def94a0df9a276a92298891f7bdd)
- [actions] use `node/install` instead of `node/run`; use `codecov` action [`1e055f9`](https://github.com/inspect-js/is-map/commit/1e055f9ea79c6c7cb6f8182e644c08ae167d358b)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `object-inspect`, `safe-publish-latest`, `tape` [`12d125e`](https://github.com/inspect-js/is-map/commit/12d125ef5bd4d6cf0468f406bf3dd3b873aa3af9)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `aud`, `auto-changelog`, `es5-shim`, `object-inspect`, `tape` [`adfb18e`](https://github.com/inspect-js/is-map/commit/adfb18ee26fa3ecadfdb16657a5423dda4248ca3)
- [actions] remove redundant finisher [`c5511b7`](https://github.com/inspect-js/is-map/commit/c5511b79c739a08f7da40b9cae2391d10b4b613c)
- [Dev Deps] update `@ljharb/eslint-config`, `aud`, `es6-shim`, `npmignore`, `object-inspect`, `tape` [`b2c7d67`](https://github.com/inspect-js/is-map/commit/b2c7d674d2e78f5fb67a7e69b83ae177255fb8da)
- [actions] update rebase action to use reusable workflow [`bbad644`](https://github.com/inspect-js/is-map/commit/bbad64428c5b777070ed86130669211ec1645714)
- [actions] update codecov uploader [`8f57f98`](https://github.com/inspect-js/is-map/commit/8f57f98d3e3897fa82e87a155f05b7fdb174c222)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `auto-changelog`, `es5-shim`, `object-inspect`, `tape` [`d330ff4`](https://github.com/inspect-js/is-map/commit/d330ff4cbdbbce8402da928cab040e2c85126506)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `aud`, `object-inspect`, `tape` [`454e31c`](https://github.com/inspect-js/is-map/commit/454e31ccecaa2ac78c7397afe2b0101576ad5b11)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `es5-shim`, `tape` [`b43283d`](https://github.com/inspect-js/is-map/commit/b43283dcd906d2024d2b78448bf8b679922d791b)
- [readme] add actions and codecov badges [`0fc119e`](https://github.com/inspect-js/is-map/commit/0fc119ed01da39b3444478f7912447f6f298339f)
- [Dev Deps] update `eslint`, `object-inspect` [`e2311f8`](https://github.com/inspect-js/is-map/commit/e2311f8984f2e2efda5011b4636275bfa7b17e8d)
- [meta] add missing `engines.node` [`9bddaf2`](https://github.com/inspect-js/is-map/commit/9bddaf20a47fc5f359d171c8a7d43ac667d4680d)
- [meta] use `prepublishOnly` script for npm 7+ [`d3b7661`](https://github.com/inspect-js/is-map/commit/d3b76613fcd34381a1ccdf17f4ab6e3e892dfc5f)
- [Dev Deps] update `safe-publish-latest` [`00d7b69`](https://github.com/inspect-js/is-map/commit/00d7b69c315b9404b49c8d0ca85774f739f25a61)
- [meta] add `sideEffects` flag [`bab4457`](https://github.com/inspect-js/is-map/commit/bab445707d11d590f2650f43b58bf9fa8dd664d1)

## [v2.0.2](https://github.com/inspect-js/is-map/compare/v2.0.1...v2.0.2) - 2020-12-13

### Commits

- [Tests] migrate tests to Github Actions [`349a036`](https://github.com/inspect-js/is-map/commit/349a0362a744d024937a4356134389cbebf0c1a7)
- [meta] do not publish github action workflow files [`f473ae7`](https://github.com/inspect-js/is-map/commit/f473ae777d15c5d247002f5aaa52ed4ada3a5dd4)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `aud`, `auto-changelog`, `es6-shim`, `object-inspect`, `tape` [`12dbda3`](https://github.com/inspect-js/is-map/commit/12dbda37a97c0dab0a3874a6cff086cd44f1c94c)
- [Tests] run `nyc` on all tests; use `tape` runner; add `core-js` tests [`b280737`](https://github.com/inspect-js/is-map/commit/b280737c513588fef4b88c16328627744c8ab946)
- [actions] add "Allow Edits" workflow [`d8dcf17`](https://github.com/inspect-js/is-map/commit/d8dcf17dd6b1cc09b8de369aa87188f469297b7c)
- [readme] remove travis badge [`eab86f9`](https://github.com/inspect-js/is-map/commit/eab86f94cca4941861784e5eb8b7ca05e847e0b5)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `tape` [`9c87af5`](https://github.com/inspect-js/is-map/commit/9c87af5008a4ff79bffc3a6de55bf2d65979db6d)
- [actions] switch Automatic Rease workflow to `pull_request_tarbget` event [`71647b8`](https://github.com/inspect-js/is-map/commit/71647b805066ecbc096d5742fd69046d22f2b5c4)
- [Dev Deps] update `es5-shim`, `tape` [`3a91230`](https://github.com/inspect-js/is-map/commit/3a912305d7d836e8d6e4f80e9047e3beff8ea887)
- [Dev Deps] update `auto-changelog`; add `aud` [`d3cd3da`](https://github.com/inspect-js/is-map/commit/d3cd3da9008756a02c2b26b45292c477bf9594a9)
- [Tests] only audit prod deps [`83ef327`](https://github.com/inspect-js/is-map/commit/83ef327c62d54a48193bf95ed8cb6c4dff0a2035)
- [meta] normalize line endings [`81a9eec`](https://github.com/inspect-js/is-map/commit/81a9eec713f8e309fa1f0ffb7e4b154c359b367b)

## [v2.0.1](https://github.com/inspect-js/is-map/compare/v2.0.0...v2.0.1) - 2019-12-17

### Fixed

- [Refactor] avoid top-level return, because babel and webpack are broken [`#5`](https://github.com/inspect-js/is-map/issues/5) [`#4`](https://github.com/inspect-js/is-map/issues/4) [`#3`](https://github.com/inspect-js/is-map/issues/3) [`#78`](https://github.com/inspect-js/node-deep-equal/issues/78) [`#7`](https://github.com/es-shims/Promise.allSettled/issues/7) [`#12`](https://github.com/airbnb/js-shims/issues/12)

### Commits

- [actions] add automatic rebasing / merge commit blocking [`743f29f`](https://github.com/inspect-js/is-map/commit/743f29fc527b4a8a56a7045ad3d56ecfc798b1a3)
- [Dev Deps] update `eslint`, `@ljharb/eslint-config`, `tape` [`8ced854`](https://github.com/inspect-js/is-map/commit/8ced854c842c86cb126b86618cb4f90ef6a04f2b)

## [v2.0.0](https://github.com/inspect-js/is-map/compare/v1.0.1...v2.0.0) - 2019-11-12

### Commits

- Initial commit [`38592bc`](https://github.com/inspect-js/is-map/commit/38592bcb928d97b244cca6cee91142a44bcf5ab1)
- Tests [`ca54632`](https://github.com/inspect-js/is-map/commit/ca546326943385052e8b5a04377f1f8b110b7306)
- readme [`9ad8bb6`](https://github.com/inspect-js/is-map/commit/9ad8bb6bc2fb295ada21e1cd901c89aa55acad37)
- implementation [`03e1dbc`](https://github.com/inspect-js/is-map/commit/03e1dbc64eb09e6caba919c9ae5662992f0a9b52)
- npm init [`d05ce8b`](https://github.com/inspect-js/is-map/commit/d05ce8b0ad797c97ed23a7730a9e211e5fe0fe92)
- [meta] add `funding` field; create `FUNDING.yml` [`2d56b4e`](https://github.com/inspect-js/is-map/commit/2d56b4e2a44e6eb4557d9d192a863c92b68c6597)
- [meta] add `safe-publish-latest`, `auto-changelog` [`2ebecb5`](https://github.com/inspect-js/is-map/commit/2ebecb5a3fe5fa682d5d04d1cd87f4d88ba22ec9)
- [Tests] add `npm run lint` [`ddc3e32`](https://github.com/inspect-js/is-map/commit/ddc3e320c3d181b9111dd3a86df486604710e08c)
- [Tests] use shared travis-ci configs [`69f6d9c`](https://github.com/inspect-js/is-map/commit/69f6d9c52a06dda27419eb41572b8db6009f6d49)
- Only apps should have lockfiles [`408cccd`](https://github.com/inspect-js/is-map/commit/408cccdc824c017547573d816b2201e9cfb9a292)
- [Tests] add `npx aud` in `posttest` [`5eadb02`](https://github.com/inspect-js/is-map/commit/5eadb02075754732df3532bc2e98ca6307c46537)

## [v1.0.1](https://github.com/inspect-js/is-map/compare/v1.0.0...v1.0.1) - 2015-07-02

### Commits

- small tweaks [`2bd7622`](https://github.com/inspect-js/is-map/commit/2bd762263930d4f72eedd3a54678e1692062d53f)
- Add `related` section to readme [`3231e74`](https://github.com/inspect-js/is-map/commit/3231e748fbf1d4d7d1662b8a559e73cc1e69468b)
- Update license info in `readme.md` [`3a03b38`](https://github.com/inspect-js/is-map/commit/3a03b387b798d5eda09965dcf63e0c9fb9c7ddac)
- editorconfig: indent yml using 2 spaces [`d724177`](https://github.com/inspect-js/is-map/commit/d724177b7eb103174cd9ca1dce4a914e3dfdb1cd)

## v1.0.0 - 2015-02-18

### Commits

- init [`73b9f38`](https://github.com/inspect-js/is-map/commit/73b9f38e3d3c0435e639a7e054714d71b6ddae9b)

