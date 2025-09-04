# AgentUp Middleware

This document explains AgentUp's universal middleware system and it's automatic / opt-out and over-ride mechanisms.

## How It Works

### 1. Configuration

A root level middleware key is defined in your `agentup.yml`:

```yaml
middleware:
  - name: timed
    config: {}
  - name: cached
    config:
      ttl: 300
  - name: rate_limited
    config:
      requests_per_minute: 60
  - name: retryable
    config:
      max_retries: 3
      backoff_factor: 2
```

This configuration defines a list of middleware to be applied globally to all endpoints and plugins.

### 2. Automatic Application

When the agent starts:

1. **Framework loads** the middleware configuration
2. **Global application** applies middleware to all existing endpoints
    - This means all handlers registered with `register_handler()` automatically receive middleware
3. **Plugin integration** ensures plugin plugins receive middleware

### 3. Available Middleware

| Middleware | Purpose | Key Parameters |
|------------|---------|----------------|
| `timed` | Track execution time | None |
| `cached` | Cache responses | `ttl` (seconds) |
| `rate_limited` | Limit request rate | `requests_per_minute` |
| `retryable` | Retry on failure | `max_retries`, `backoff_factor` |


## Per-Plugin Override

Each Middleware feature can be overridden for specific plugins using the `plugin_override` field.

This allows you to customize middleware behavior for individual plugins, depending on their specific needs.

### Plugin Middleware Override Structure

The exact structure for plugin middleware override is:

```yaml
plugins:
  - plugin_id: your_plugin_id
    # ... other plugin configuration
    plugin_override:  # List of MiddlewareOverride objects
      - name: middleware_name        # Required: alphanumeric with hyphens/underscores
        config:                      # Optional: middleware-specific configuration dict
          key: value
      - name: another_middleware
        config: {}
```

### Available Middleware Types

The system supports these middleware types (from `src/agent/services/middleware.py`):

- **`timed`** - Execution timing (no configuration required)
- **`cached`** - Response caching (uses `CacheConfig` model)
- **`rate_limited`** - Request rate limiting (uses `RateLimitConfig` model)  
- **`retryable`** - Retry logic on failures (uses `RetryConfig` model)

### Override Behavior

Plugin middleware overrides work through **complete replacement**:

1. **Complete Replacement**: Define a new set of middleware that replaces the global configuration for that plugin
2. **Selective Exclusion**: Specify only the middleware you want to apply, excluding others
3. **Empty Override**: Use an empty `plugin_override: []` to disable all middleware for that plugin

### Example Configurations

Let's assume we have the following global middleware configuration:

```yaml
# Global middleware for all handlers
middleware:
  - name: timed
    config: {}
  - name: cached
    config: {ttl: 300}  # 5 minutes default
  - name: rate_limited
    config: {requests_per_minute: 60}
  - name: retryable
    config: {max_retries: 3, backoff_factor: 2}
```

For a specific plugin, you can override this behavior, for example, to disable caching and change the rate limit:

```yaml
plugins:
  - plugin_id: expensive_operation
    name: Expensive Operation
    description: A resource-intensive operation
    plugin_override:
      - name: cached
        config: {ttl: 3600}  # 1 hour for this specific plugin
      - name: rate_limited
        config:
          requests_per_minute: 120  # higher rate limit for this plugin
```

### How Per-Plugin Overrides Work

The `MiddlewareManager.get_middleware_for_plugin()` method handles plugin-specific overrides:

1. **Global middleware** is defined in the top-level `middleware` section
2. **Plugin override detection** - checks for `plugin_override` in plugin configuration
3. **Complete replacement** - if `plugin_override` exists, it replaces the global configuration entirely
4. **Fallback behavior** - if no override exists, uses global middleware configuration
5. **Order matters** - middleware in the override is applied in the specified order
6. **Validation** - middleware names must be alphanumeric with hyphens/underscores only

**Implementation Reference:** `src/agent/services/middleware.py:65-74`

### Use Cases for Per-Plugin Overrides

1. **Different Cache TTLs**:
   ```yaml
   plugins:
     weather_api:
       plugin_override:
         - name: cached
           config: {ttl: 1800}  # 30 minutes for weather data
   ```

2. **Disable Caching for Real-time Data**:
   ```yaml
   plugins:
     stock_ticker:
       plugin_override:
         - name: timed
           config: {}
         # No caching middleware
   ```

3. **Higher Rate Limits for Admin Functions**:
   ```yaml
   plugins:
     admin_panel:
       plugin_override:
         - name: rate_limited
           config: {requests_per_minute: 300}  # Higher limit
   ```

4. **Disable All Middleware**:
   ```yaml
   plugins:
     raw_performance:
       plugin_override: []  # Empty array disables all middleware
   ```

### Selectively Excluding Middleware

```yaml
plugins:
  - plugin_id: no_cache_plugin
    plugin_override:
      - name: timed
        config: {}
      - name: rate_limited
        config: {requests_per_minute: 60}
      # Note: No caching middleware listed

  # This plugin gets ONLY logging
  - plugin_id: minimal_plugin
    plugin_override:
      - name: timed
        config: {}

  # This plugin gets NO middleware at all
  - plugin_id: bare_metal_plugin
    plugin_override: []
```

Since `plugin_override` completely replaces the global middleware, you can exclude specific
middleware by simply not including them:

```yaml
# Global middleware
middleware:
  - name: timed
    config: {}
  - name: cached
    config: {ttl: 300}
  - name: rate_limited
    config: {requests_per_minute: 60}

plugins:
  # This skill gets everything EXCEPT caching
  - plugin_id: no_cache_skill
    plugin_override:
      - name: timed
        config: {}
      - name: rate_limited
        config: {requests_per_minute: 60}
      # Note: No caching middleware listed

  # This skill gets ONLY logging
  - plugin_id: minimal_skill
    plugin_override:
      - name: timed
        config: {}

  # This skill gets NO middleware at all
  - plugin_id: bare_metal_skill
    plugin_override: []
```

## Validation

Use `agentup validate` to check middleware configuration:

```bash
$ agentup validate
✓ Middleware configuration validated (5 middleware items)
```

## Troubleshooting

### Middleware Not Applied

1. **Check configuration** - Ensure `middleware` section exists in `agentup.yml`
2. **Validate syntax** - Use `agentup validate`

### Performance Issues

1. **Order matters** - Put caching before expensive middleware
2. **Tune parameters** - Adjust rate limits and cache TTLs
3. **Monitor metrics** - Use timing middleware to identify bottlenecks

## Best Practices

1. **Start minimal** - Add middleware incrementally
2. **Monitor impact** - Use timing middleware to measure
3. **Cache wisely** - Not all handlers benefit from caching
4. **Rate limit appropriately** - Balance protection vs usability
5. **Log judiciously** - INFO level for production, DEBUG for development
