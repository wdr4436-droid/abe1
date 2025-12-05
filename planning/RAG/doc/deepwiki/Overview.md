# Overview

> **Relevant source files**
> * [.github/workflows/ci.yml](https://github.com/JHUISI/charm/blob/7b52fa53/.github/workflows/ci.yml)
> * [README.md](https://github.com/JHUISI/charm/blob/7b52fa53/README.md)
> * [charm/schemes/pkenc/pkenc_paillier99.py](https://github.com/JHUISI/charm/blob/7b52fa53/charm/schemes/pkenc/pkenc_paillier99.py)
> * [charm/test/schemes/pkenc_test.py](https://github.com/JHUISI/charm/blob/7b52fa53/charm/test/schemes/pkenc_test.py)
> * [doc/Makefile](https://github.com/JHUISI/charm/blob/7b52fa53/doc/Makefile)
> * [doc/autoschemes.py](https://github.com/JHUISI/charm/blob/7b52fa53/doc/autoschemes.py)
> * [doc/config.py](https://github.com/JHUISI/charm/blob/7b52fa53/doc/config.py)
> * [doc/source/conf.py](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/conf.py)
> * [doc/source/index.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/index.rst)
> * [doc/source/install_source.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/install_source.rst)
> * [doc/source/schemes.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/schemes.rst)
> * [doc/source/toolbox.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/toolbox.rst)
> * [doc/source/tutorial.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/tutorial.rst)

## Purpose and Scope

This document provides a high-level introduction to the Charm-Crypto framework, covering its architecture, core components, and system organization. Charm is a framework for rapidly prototyping advanced cryptographic systems, combining high-performance C modules for mathematical operations with Python-based scheme implementations.

For detailed installation procedures, see [Installation and Build System](/JHUISI/charm/2-installation-and-build-system). For in-depth coverage of the mathematical foundation, see [Core Mathematical Foundation](/JHUISI/charm/3-core-mathematical-foundation). For guidance on implementing new schemes, see [Application Development](/JHUISI/charm/7-application-development).

## What is Charm-Crypto

Charm-Crypto is a hybrid cryptographic framework designed to minimize development time and code complexity while maximizing performance for cryptographic operations. The system uses a two-layer architecture: performance-critical mathematical operations are implemented in native C modules, while cryptographic schemes themselves are written in Python for readability and rapid prototyping.

**Key Capabilities:**

* Support for integer rings/fields, bilinear and non-bilinear elliptic curve groups
* Base cryptographic library including symmetric encryption, hash functions, and PRNGs
* Standard APIs for digital signatures, encryption, and commitment schemes
* Protocol engine for implementing multi-party cryptographic protocols
* Integrated compiler for interactive and non-interactive zero-knowledge proofs
* Built-in benchmarking and testing capabilities

**Sources:** [README.md L8-L18](https://github.com/JHUISI/charm/blob/7b52fa53/README.md#L8-L18)

## System Architecture Overview

The following diagram illustrates the overall system architecture, showing how the major components interact:

### High-Level Component Architecture

```

```

**Sources:** [README.md L8-L18](https://github.com/JHUISI/charm/blob/7b52fa53/README.md#L8-L18)

 [doc/source/schemes.rst L1-L67](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/schemes.rst#L1-L67)

 [doc/source/toolbox.rst L1-L49](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/toolbox.rst#L1-L49)

## Core Framework Components

### Mathematical Foundation Modules

The performance-critical components are implemented as C extensions that provide Python bindings to external cryptographic libraries:

| Module | File | Purpose | Backend Libraries |
| --- | --- | --- | --- |
| Pairing Operations | `pairingmodule.c` | Bilinear pairing computations | PBC, RELIC, MIRACL |
| Elliptic Curves | `ecmodule.c` | EC point operations | OpenSSL |
| Integer Arithmetic | `integermodule.c` | Big integer operations | GMP |
| Benchmarking | `benchmarkmodule.c` | Performance measurement | N/A |

### Python Toolbox Layer

The Python toolbox provides high-level abstractions that wrap the C modules:

* **`PairingGroup`**: Interface for pairing-based cryptography operations
* **`ECGroup`**: Elliptic curve group operations and point arithmetic
* **`IntegerGroup`**: Integer group operations for RSA and Schnorr schemes
* **`SymmetricCrypto`**: Symmetric encryption and hash functions

### Cryptographic Schemes

Charm includes implementations of numerous cryptographic schemes organized by category:

* **Attribute-Based Encryption (ABE)**: `charm/schemes/abenc/` directory
* **Public-Key Encryption**: `charm/schemes/pkenc/` directory
* **Public-Key Signatures**: `charm/schemes/pksig/` directory
* **Identity-Based Encryption**: `charm/schemes/ibenc/` directory

**Sources:** [doc/source/toolbox.rst L10-L47](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/toolbox.rst#L10-L47)

 [doc/source/schemes.rst L7-L64](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/schemes.rst#L7-L64)

 [doc/autoschemes.py L123-L127](https://github.com/JHUISI/charm/blob/7b52fa53/doc/autoschemes.py#L123-L127)

## Code Organization and Key Entry Points

The following diagram maps the major system concepts to their concrete implementations in the codebase:

### Code Entity Mapping

```

```

**Sources:** [charm/test/schemes/pkenc_test.py L8-L12](https://github.com/JHUISI/charm/blob/7b52fa53/charm/test/schemes/pkenc_test.py#L8-L12)

 [doc/autoschemes.py L11-L31](https://github.com/JHUISI/charm/blob/7b52fa53/doc/autoschemes.py#L11-L31)

 [doc/source/tutorial.rst L14-L33](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/tutorial.rst#L14-L33)

## Installation and Dependencies

Charm requires several external libraries for mathematical operations:

**Core Dependencies:**

* **GMP 5.x**: Big integer arithmetic (`integermodule.c` dependency)
* **PBC 0.5.14**: Pairing-based cryptography (`pairingmodule.c` dependency)
* **OpenSSL**: Elliptic curve operations (`ecmodule.c` dependency)
* **PyParsing 2.1.5**: Policy parsing for attribute-based schemes
* **Hypothesis**: Property-based testing framework

**Optional Libraries:**

* **MIRACL**: Alternative mathematical backend
* **RELIC**: Alternative cryptographic toolkit

The build process is automated through `configure.sh` which detects the environment and generates appropriate build configurations, followed by `make` and `make install`.

**Sources:** [README.md L38-L51](https://github.com/JHUISI/charm/blob/7b52fa53/README.md#L38-L51)

 [doc/source/install_source.rst L10-L26](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/install_source.rst#L10-L26)

## Development Workflow

Charm supports multiple development scenarios:

1. **Using Existing Schemes**: Import and instantiate implemented cryptographic schemes
2. **Implementing New Schemes**: Extend base classes like `PKEnc`, `ABEnc`, or `PKSig`
3. **Embedding in Applications**: Use the C/C++ embedding API for native integration
4. **Contributing Schemes**: Follow the testing and documentation requirements for inclusion

Each cryptographic scheme includes a `main` function demonstrating usage, and comprehensive test suites ensure correctness. The framework includes automatic documentation generation through `autoschemes.py` which creates documentation stubs for new schemes.

**Sources:** [doc/source/tutorial.rst L117-L136](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/tutorial.rst#L117-L136)

 [README.md L24-L34](https://github.com/JHUISI/charm/blob/7b52fa53/README.md#L24-L34)

 [doc/autoschemes.py L91-L116](https://github.com/JHUISI/charm/blob/7b52fa53/doc/autoschemes.py#L91-L116)

## Testing and Quality Assurance

The framework includes multiple testing approaches:

* **Unit Tests**: Traditional test cases for individual components
* **Property-Based Testing**: Using Hypothesis for automatic test case generation
* **Continuous Integration**: GitHub Actions workflow for automated testing
* **Benchmarking**: Performance measurement capabilities through `benchmarkmodule.c`

Tests are organized in the `charm/test/` directory with separate subdirectories for scheme tests and toolbox tests.

**Sources:** [.github/workflows/ci.yml

1-49](https://github.com/JHUISI/charm/blob/7b52fa53/.github/workflows/ci.yml#L1-L49)

 [charm/test/schemes/pkenc_test.py L18-L251](https://github.com/JHUISI/charm/blob/7b52fa53/charm/test/schemes/pkenc_test.py#L18-L251)