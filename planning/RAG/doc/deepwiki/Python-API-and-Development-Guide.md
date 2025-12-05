# Python API and Development Guide

> **Relevant source files**
> * [doc/source/cryptographers.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst)
> * [doc/source/developers.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/developers.rst)
> * [doc/source/miracl.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/miracl.rst)
> * [doc/source/mobile.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/mobile.rst)
> * [doc/source/relic.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/relic.rst)
> * [doc/source/updates.rst](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/updates.rst)

This guide provides comprehensive documentation for Python developers working with Charm-Crypto, covering both the implementation of new cryptographic schemes and the integration of existing schemes into applications. It focuses on the high-level Python abstractions, group theory foundations, API patterns, and development best practices.

For information about integrating Charm-Crypto into C/C++ applications, see [C/C++ Embedding API](/JHUISI/charm/7.2-cc++-embedding-api). For details about the underlying mathematical foundations, see [Core Mathematical Foundation](/JHUISI/charm/3-core-mathematical-foundation).

## Group Abstractions

Charm-Crypto's Python API is built around mathematical group abstractions that provide the foundation for cryptographic scheme implementation. These abstractions encapsulate the complexity of underlying cryptographic libraries while providing a consistent interface.

### Core Group Types

```

```

**Group Initialization Patterns**

The three primary group types serve different cryptographic settings:

| Group Type | Use Cases | Key Features |
| --- | --- | --- |
| `PairingGroup` | ABE, IBE, BLS signatures | Bilinear pairings, multiple subgroups |
| `ECGroup` | ECDSA, ECDH, EC-based PKE | Elliptic curve operations, NIST curves |
| `IntegerGroup` | RSA, DSA, Schnorr | Large integer arithmetic, safe primes |

Sources: [doc/source/cryptographers.rst L11-L30](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L11-L30)

### PairingGroup API

The `PairingGroup` class provides access to pairing-based cryptography with symmetric and asymmetric curve support:

```

```

Sources: [doc/source/cryptographers.rst L24-L30](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L24-L30)

### ECGroup API

The `ECGroup` class supports NIST-approved elliptic curves for standard public-key operations:

```

```

Sources: [doc/source/cryptographers.rst L41-L54](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L41-L54)

### IntegerGroup API

The `IntegerGroup` class provides large integer arithmetic for RSA and discrete logarithm schemes:

```

```

Sources: [doc/source/cryptographers.rst L17-L23](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L17-L23)

## Scheme Implementation Patterns

Charm-Crypto follows object-oriented design patterns for cryptographic scheme implementation, with base classes providing standardized interfaces for different primitive types.

### Base Class Hierarchy

```

```

Sources: [doc/source/cryptographers.rst L38-L48](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L38-L48)

### Scheme Implementation Template

The following pattern demonstrates implementing a PKE scheme inheriting from the `PKEnc` base class:

```

```

Sources: [doc/source/cryptographers.rst L43-L135](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L43-L135)

### Algorithm Implementation Patterns

Key implementation patterns for cryptographic algorithms:

| Pattern | Usage | Example |
| --- | --- | --- |
| Random Element Generation | `group.random(domain)` | `g = group.random(G1)` |
| Exponentiation | `base ** exponent` | `g ** x` |
| Group Operations | `*` (multiplication), `/` (division) | `g1 * g2`, `c / h` |
| Hashing | `group.hash(data)` | `alpha = group.hash((u1, u2, e))` |
| Encoding/Decoding | `group.encode()`, `group.decode()` | Convert messages to group elements |

Sources: [doc/source/cryptographers.rst L82-L134](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L82-L134)

## Using Existing Schemes

Charm-Crypto provides numerous pre-implemented cryptographic schemes that can be directly integrated into applications.

### Scheme Instantiation Pattern

```

```

### Example Usage

Standard pattern for using an existing PKE scheme:

```

```

Sources: [doc/source/developers.rst L14-L26](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/developers.rst#L14-L26)

## Serialization API

Charm-Crypto provides robust serialization capabilities for persistent storage and network transmission of cryptographic objects.

### Core Serialization Functions

The primary serialization API supports complex Python data structures containing Charm objects:

```

```

Sources: [doc/source/developers.rst L39-L43](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/developers.rst#L39-L43)

### Custom Serialization

For schemes using integer groups that don't require a group object:

```

```

Sources: [doc/source/developers.rst L51-L72](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/developers.rst#L51-L72)

### Serialization Security

Charm-Crypto has migrated from Pickle-based serialization to JSON-based serialization for security reasons. Pickle methods are still available but deprecated due to vulnerability to arbitrary code execution.

Sources: [doc/source/updates.rst L31-L34](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/updates.rst#L31-L34)

## Benchmarking and Performance

Charm-Crypto provides comprehensive benchmarking capabilities integrated into group abstractions for performance measurement and optimization.

### Benchmarking API

```

```

### Basic Benchmarking Example

```

```

Sources: [doc/source/cryptographers.rst L156-L182](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L156-L182)

### Pairing Group Benchmarking

For pairing-based cryptography with granular operation counting:

```

```

Sources: [doc/source/cryptographers.rst L188-L212](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L188-L212)

### Performance Optimizations

**Pre-computation Tables**: For repeated exponentiations with the same base, use pre-computation tables:

```

```

Sources: [doc/source/cryptographers.rst L237-L263](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L237-L263)

## Testing and Development Workflow

### Testing Patterns

Charm-Crypto supports multiple testing approaches:

1. **Docstring Tests**: Embed tests directly in scheme class docstrings
2. **Standalone Test Functions**: Implement `main()` functions that demonstrate scheme usage
3. **Unit Tests**: Use Python's unittest framework
4. **Property-Based Testing**: Leverage Hypothesis for comprehensive testing

### Development Best Practices

| Practice | Implementation | Benefit |
| --- | --- | --- |
| Algorithm Validation | Compare against test vectors | Correctness verification |
| Performance Benchmarking | Use built-in benchmark API | Performance optimization |
| Serialization Testing | Test key/ciphertext persistence | Data integrity |
| Error Handling | Validate inputs and handle edge cases | Robustness |
| Documentation | Include usage examples and docstrings | Maintainability |

Sources: [doc/source/cryptographers.rst L147-L151](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L147-L151)

## API Reference Summary

### Core Group Classes

| Class | Module | Purpose |
| --- | --- | --- |
| `PairingGroup` | `charm.toolbox.pairinggroup` | Pairing-based cryptography |
| `ECGroup` | `charm.toolbox.ecgroup` | Elliptic curve operations |
| `IntegerGroup` | `charm.toolbox.integergroup` | Large integer arithmetic |

### Base Scheme Classes

| Class | Module | Schemes |
| --- | --- | --- |
| `PKEnc` | `charm.schemes.pkenc.pkenc` | Public-key encryption |
| `PKSig` | `charm.schemes.pksig.pksig` | Public-key signatures |
| `ABEnc` | `charm.schemes.abenc.abenc` | Attribute-based encryption |
| `IBEnc` | `charm.schemes.ibenc.ibenc` | Identity-based encryption |

### Utility Functions

| Function | Module | Purpose |
| --- | --- | --- |
| `objectToBytes()` | `charm.core.engine.util` | Serialize Charm objects |
| `bytesToObject()` | `charm.core.engine.util` | Deserialize Charm objects |
| `pair()` | `charm.toolbox.pairinggroup` | Bilinear pairing operation |

Sources: [doc/source/cryptographers.rst L1-L266](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/cryptographers.rst#L1-L266)

 [doc/source/developers.rst L1-L129](https://github.com/JHUISI/charm/blob/7b52fa53/doc/source/developers.rst#L1-L129)