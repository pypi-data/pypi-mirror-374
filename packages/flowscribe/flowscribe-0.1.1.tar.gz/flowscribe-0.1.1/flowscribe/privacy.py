def redact_and_limit(data, redact_keys, payload_limit):
	result = {}
	for k, v in data.items():
		if k in redact_keys:
			result[k] = "***REDACTED***"
		elif isinstance(v, str) and len(v) > payload_limit:
			result[k] = v[:payload_limit] + " ...[truncated]"
		else:
			result[k] = v
	return result
