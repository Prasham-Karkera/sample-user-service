# ADR-001: Use BCrypt for Password Hashing

**Status:** ACCEPTED  
**Date:** 2026-01-15  
**Author(s):** @prasham-dev  
**Deciders:** @prasham-dev, @security-lead  

---

## Context

We needed to choose a password hashing algorithm for user authentication. FleetBite requirements:
- Resistant to brute-force and rainbow table attacks
- Adjustable cost factor to stay ahead of hardware improvements
- Wide ecosystem support and audited libraries

## Decision

Use **BCrypt** via `passlib[bcrypt]` (Python) for all password hashing.

## Rationale

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| BCrypt | Battle-tested, adaptive cost, wide support | Slower than Argon2 | ✅ Selected |
| Argon2 | Winner of PHC, memory-hard | Newer, less library support | ❌ Deferred to ADR-002 |
| SHA-256 (salted) | Fast | Not designed for passwords, brute-forceable | ❌ Rejected |
| PBKDF2 | FIPS-approved | Weaker than Argon2/BCrypt | ❌ Rejected |

## Consequences

- Default cost factor: 12 (benchmarked at ~300ms on standard hardware)
- Plan to migrate to Argon2id in v2 — see ADR-002
- All password verification uses `passlib.CryptContext` for algorithm agility

## Implementation Notes

```python
from passlib.context import CryptContext
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

## References

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [passlib docs](https://passlib.readthedocs.io)
