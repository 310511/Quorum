package chi

import (
	"net/http"
	"time"
)

// RouteMetric contains information about a route hit
type RouteMetric struct {
	// Pattern is the route pattern that was matched
	Pattern string

	// Method is the HTTP method used
	Method string

	// Path is the actual request path
	Path string

	// Duration is how long the request took to process
	Duration time.Duration

	// Params contains any URL parameters
	Params map[string]string
}

// MetricsCollector defines an interface for collecting router metrics
type MetricsCollector interface {
	// RecordHit records a hit on a particular route
	RecordHit(ctx *Context, r *http.Request, duration time.Duration)
}

// SimpleMetricsCollector is a basic implementation of MetricsCollector
type SimpleMetricsCollector struct {
	OnHit func(metric RouteMetric)
}

// RecordHit implements the MetricsCollector interface
func (s *SimpleMetricsCollector) RecordHit(ctx *Context, r *http.Request, duration time.Duration) {
	params := make(map[string]string)
	for i, key := range ctx.URLParams.Keys {
		params[key] = ctx.URLParams.Values[i]
	}

	s.OnHit(RouteMetric{
		Pattern:  ctx.RoutePattern(),
		Method:   r.Method,
		Path:     r.URL.Path,
		Duration: duration,
		Params:   params,
	})
}
