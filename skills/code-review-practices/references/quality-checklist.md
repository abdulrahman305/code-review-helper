# Code Quality Review Checklist

## Logic and Correctness

### Control Flow
- [ ] All branches of conditionals are reachable
- [ ] Switch/match statements have default/exhaustive cases
- [ ] Loops have proper termination conditions
- [ ] Recursive functions have proper base cases
- [ ] Early returns don't skip necessary cleanup

### Data Handling
- [ ] Null/undefined checks before dereferencing
- [ ] Array bounds checking before access
- [ ] Type coercion is intentional and safe
- [ ] Numeric overflow/underflow considered
- [ ] Division by zero prevented

### Error Handling
- [ ] All thrown exceptions are caught appropriately
- [ ] Error messages are informative (not exposing internals)
- [ ] Failed operations don't leave partial state
- [ ] Retries have backoff and limits
- [ ] Errors are logged with sufficient context

### Concurrency
- [ ] Shared state is properly synchronized
- [ ] No race conditions in read-modify-write operations
- [ ] Deadlock potential evaluated
- [ ] Thread-safe collections used where needed
- [ ] Async operations properly awaited

## Design Quality

### Single Responsibility
- [ ] Each class/module has one clear purpose
- [ ] Functions do one thing well
- [ ] Changes to one feature don't affect unrelated code

### Open/Closed
- [ ] New features extend rather than modify existing code
- [ ] Plugin/extension points exist where variation expected

### Liskov Substitution
- [ ] Subclasses can substitute for base classes
- [ ] Overridden methods maintain contracts

### Interface Segregation
- [ ] Interfaces are focused and minimal
- [ ] Clients don't depend on unused methods

### Dependency Inversion
- [ ] High-level modules don't depend on low-level details
- [ ] Dependencies are injected, not created internally

## Code Style

### Naming
- [ ] Names describe intent, not implementation
- [ ] Consistent naming conventions throughout
- [ ] No ambiguous abbreviations
- [ ] Boolean names imply true/false meaning (isValid, hasPermission)
- [ ] Functions named with verbs, variables with nouns

### Structure
- [ ] Functions under 50 lines (ideally under 20)
- [ ] Nesting under 4 levels
- [ ] Related code grouped together
- [ ] Consistent file organization

### Comments
- [ ] Comments explain "why", not "what"
- [ ] No commented-out code
- [ ] TODOs have context and tracking
- [ ] Public API documentation complete

## Testability

### Test Coverage
- [ ] Happy path tested
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] Integration points tested

### Test Quality
- [ ] Tests are deterministic
- [ ] Tests are independent
- [ ] Test names describe behavior
- [ ] Assertions are specific and meaningful

### Design for Testing
- [ ] Dependencies are injectable
- [ ] Side effects are isolatable
- [ ] Time-dependent code uses clock abstraction
