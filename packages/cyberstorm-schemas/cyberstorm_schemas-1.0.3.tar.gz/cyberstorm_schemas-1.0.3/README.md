# Cyberstorm Schemas

> **Building Verifiable Professional Reputation as an Asset Class**

[![CI](https://github.com/cyberstorm-dev/schemas/workflows/CI/badge.svg)](https://github.com/cyberstorm-dev/schemas/actions)
[![NPM Version](https://img.shields.io/npm/v/@cyberstorm/schemas)](https://www.npmjs.com/package/@cyberstorm/schemas)
[![PyPI Version](https://img.shields.io/pypi/v/cyberstorm-schemas)](https://pypi.org/project/cyberstorm-schemas/)
[![Go Module Version](https://img.shields.io/github/v/tag/cyberstorm-dev/schemas)](https://pkg.go.dev/github.com/cyberstorm-dev/schemas)

## The Vision: Your Code Contributions as Verifiable Assets

In today's digital economy, developers build their careers through contributions to open source projects, but this professional reputation is **trapped within platforms** and **impossible to verify** across contexts. What if your GitHub contributions, code reviews, and technical expertise could become **portable, verifiable assets** that follow you throughout your career?

**Cyberstorm Schemas** provide the foundational data structures for building this future—where every meaningful contribution to software projects becomes a cryptographically-verified credential that developers truly own.

## Monorepo Architecture

This repository contains two complementary Protocol Buffer modules that power the Cyberstorm ecosystem:

### 🏛️ [Attestor Module](cyberstorm/attestor/v1/README.md)
**The Reputation Engine** - Core schemas for building verifiable professional reputation:

- **Identity System**: Cryptographic linkage between GitHub accounts and Ethereum addresses
- **Repository Registry**: On-chain repository registration with ownership proofs
- **Contribution Tracking**: Structured data for PRs, issues, and code reviews
- **Webhook Processing**: Real-time event processing from GitHub to blockchain

📋 **BSR**: [`buf.build/cyberstorm/attestor`](https://buf.build/cyberstorm/attestor)

### 🔐 [Crypto Module](cyberstorm/crypto/v1/README.md)
**IPLD Cryptographic Primitives** - Content-addressed data structures:

- **Content Identifiers (CID)**: Self-describing content addressing
- **Encryption Keys**: CEK/KEK management for secure content
- **Context References**: Building verifiable content graphs through IPLD links
- **Modern Standards**: ChaCha20-Poly1305 for EVM ecosystems

📋 **BSR**: [`buf.build/cyberstorm/crypto`](https://buf.build/cyberstorm/crypto)

## How It Works: The Three-Step Reputation Network

### 1. **Decentralized Identity (DID) Registration**
Verifiably link your GitHub account to an Ethereum address, creating a cryptographic bridge between your development identity and blockchain-based credentials.

### 2. **Repository Registration** 
Project maintainers register their repositories on-chain, establishing them as legitimate sources of verifiable contributions within the reputation network.

### 3. **Contribution Attestation**
High-value contributions—pull requests, issue resolutions, code reviews—against registered repositories, by registered identities, are automatically attested on-chain through the [cyberstorm-attestor](https://github.com/cyberstorm-dev/attestor) service.

## Why This Matters for Developers

- **Portable Reputation**: Your verified contributions follow you across companies, platforms, and careers
- **Proof of Expertise**: Demonstrate technical skills with cryptographic proof, not just claims  
- **Network Effects**: Join an ecosystem where verified reputation creates measurable professional value
- **Future-Proof Career**: Build assets that appreciate as the reputation network grows

## Installation & Integration

### Recommended: Buf Schema Registry

**Attestor Module**
```bash
buf generate buf.build/cyberstorm/attestor
```

**Crypto Module**
```bash
buf generate buf.build/cyberstorm/crypto
```

**Add as Dependencies**
```yaml
# buf.yaml
deps:
  - buf.build/cyberstorm/attestor
  - buf.build/cyberstorm/crypto
```

### Legacy Package Managers

**TypeScript/JavaScript**
```bash
npm install @cyberstorm/schemas
```

**Python**
```bash
pip install cyberstorm-schemas
```

**Go**
```bash
go get github.com/cyberstorm-dev/schemas
```

## Usage Examples

### Identity Registration (Attestor Module)

**TypeScript/JavaScript**
```typescript
import { Identity, Domain } from 'buf.build/cyberstorm/attestor';

// Register a GitHub identity with Ethereum address
const identity = new Identity({
  domain: new Domain({
    name: 'GitHub',
    domain: 'github.com'
  }),
  identifier: 'developer123',
  registrant: '0x742d35Cc6634C0532925a3b8D16f5a2C01234567',
  proofUrl: 'https://gist.github.com/developer123/abc123...',
  validator: '0x8ba1f109551bD432803012645Hac189451c24567'
});
```

### Content Addressing (Crypto Module)

**Python**
```python
from cyberstorm.crypto.v1 import CID, ContentEncryptionKey, EncryptionType

# Create self-describing content identifier
content_cid = CID(
    cid="bafkreig6mqa4p36x77qf5r3r7n4n4k3q3q3q3q3q3q3q3q3q3q3q3q3q"
)

# Set up content encryption
cek = ContentEncryptionKey(
    type=EncryptionType.ENCRYPTION_TYPE_CHACHA20_POLY1305,
    encrypted_key=b"encrypted_content_key_bytes..."
)
```

### Repository Registration (Attestor Module)

**Go**
```go
import attestorv1 "buf.build/cyberstorm/attestor/cyberstorm/attestor/v1"

// Register a repository for contribution tracking
repoRegistration := &attestorv1.Repository{
    Repository: &attestorv1.Repository{
        Domain: &attestorv1.Domain{
            Name:   "GitHub",
            Domain: "github.com",
        },
        Path: "awesome-org/amazing-project",
    },
    Registrant: registeredIdentity,
    ProofUrl:   "https://github.com/awesome-org/amazing-project/issues/42",
}
```

## Getting Started: Join the Reputation Network

Ready to build verifiable professional reputation? Here's how to integrate these schemas into your development workflow:

### For Repository Maintainers

Use [cyberstorm-attestor-client](https://github.com/cyberstorm-dev/attestor-client) to:

1. **Register your repository** using the `Repository` schema
2. **Configure webhooks** to automatically attest contributor actions
3. **Build value** for your community by making contributions verifiable

### For Developers

Use [cyberstorm-attestor-client](https://github.com/cyberstorm-dev/attestor-client) to:

1. **Register your identity** linking GitHub to your Ethereum address
2. **Contribute to registered repositories** and earn verified attestations
3. **Build portable reputation** that transcends individual platforms

### For Platform Builders
1. **Import these schemas** to build reputation-aware applications
2. **Query attestations** to understand developer expertise and activity  
3. **Create network effects** by recognizing verified contributions

## Built for Scale

- **🌐 Multi-language client libraries** for seamless integration
- **🛡️ EAS-compatible schemas** built on Ethereum Attestation Service
- **🧰 buf.build toolchain** for professional Protocol Buffer development  
- **🤖 Comprehensive CI/CD** with automated testing and publishing
- **📊 Production-ready** data structures for enterprise adoption

## Documentation

- **[Development Setup](docs/DEVELOPMENT.md)** - Complete setup guide for all platforms and IDEs
- **[Contributing](docs/CONTRIBUTING.md)** - Guidelines for contributing to the project
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Solutions for common issues
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Commands, imports, and schema overview

## The Future of Professional Reputation

**Traditional Model**: Your contributions are trapped within platforms, easily lost, and impossible to verify across contexts.

**Cyberstorm Model**: Your contributions become cryptographically-verified credentials that create measurable professional value and follow you throughout your career.

### Join the Network

The value of the reputation network grows with each participant:

- **More registered repositories** = More opportunities to earn verifiable credentials
- **More registered developers** = Stronger network effects and reputation signals  
- **More platform adoption** = Greater utility for verified contributions

**Ready to build the future?** Start by integrating these schemas into your applications and contributing to the growing ecosystem of verifiable professional reputation.

### Related Projects

- **[cyberstorm-attestor](https://github.com/cyberstorm-dev/cyberstorm-attestor)**: The service that processes GitHub webhooks and creates attestations using these schemas
- **[Ethereum Attestation Service (EAS)](https://attest.sh/)**: The underlying attestation infrastructure
- **Protocol Buffer Ecosystem**: Learn more about [buf.build](https://buf.build/) for professional Protocol Buffer development

## License

MIT

## Contact

For questions or support, please open an issue on GitHub.