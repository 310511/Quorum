package chi

import (
	"net/http"
	"strings"
)

// RouteSelector allows dynamic selection of handlers based on request properties
type RouteSelector interface {
	// SelectRoute chooses a handler based on the request and the matched pattern
	SelectRoute(r *http.Request, pattern string, handler http.Handler) http.Handler
}

// RouteTransformer allows modification of handlers after selection
type RouteTransformer interface {
	// TransformHandler wraps or replaces a handler based on request properties
	TransformHandler(r *http.Request, pattern string, handler http.Handler) http.Handler
}

// VersionSelector implements RouteSelector to provide API versioning
type VersionSelector struct {
	// DefaultVersion is used if no version is specified in the request
	DefaultVersion string

	// Handlers maps versions to their specific handlers
	Handlers map[string]map[string]http.Handler
}

// NewVersionSelector creates a new version selector with the given default version
func NewVersionSelector(defaultVersion string) *VersionSelector {
	return &VersionSelector{
		DefaultVersion: defaultVersion,
		Handlers:       make(map[string]map[string]http.Handler),
	}
}

// AddHandler registers a handler for a specific route pattern and version
func (vs *VersionSelector) AddHandler(pattern, version string, handler http.Handler) {
	if vs.Handlers[pattern] == nil {
		vs.Handlers[pattern] = make(map[string]http.Handler)
	}
	vs.Handlers[pattern][version] = handler
}

// SelectRoute implements RouteSelector interface
func (vs *VersionSelector) SelectRoute(r *http.Request, pattern string, defaultHandler http.Handler) http.Handler {
	// Extract version from Accept header or query param
	version := r.URL.Query().Get("version")
	if version == "" {
		accept := r.Header.Get("Accept")
		if strings.Contains(accept, "version=") {
			parts := strings.Split(accept, "version=")
			if len(parts) > 1 {
				version = strings.Split(parts[1], ";")[0]
			}
		}
	}

	// If no version found, use default
	if version == "" {
		version = vs.DefaultVersion
	}

	// Find handler for this pattern and version
	if vs.Handlers[pattern] != nil && vs.Handlers[pattern][version] != nil {
		return vs.Handlers[pattern][version]
	}

	return defaultHandler
}

// RoleBasedSelector implements RouteSelector to provide role-based routing
type RoleBasedSelector struct {
	// RoleExtractor is a function that determines the user's role from the request
	RoleExtractor func(r *http.Request) string

	// DefaultRole is used when no role can be determined from the request
	DefaultRole string

	// Handlers maps roles to their specific handlers for each pattern
	Handlers map[string]map[string]http.Handler
}

// NewRoleBasedSelector creates a new role-based selector
func NewRoleBasedSelector(roleExtractor func(r *http.Request) string, defaultRole string) *RoleBasedSelector {
	return &RoleBasedSelector{
		RoleExtractor: roleExtractor,
		DefaultRole:   defaultRole,
		Handlers:      make(map[string]map[string]http.Handler),
	}
}

// AddHandler registers a handler for a specific route pattern and role
func (rs *RoleBasedSelector) AddHandler(pattern, role string, handler http.Handler) {
	if rs.Handlers[pattern] == nil {
		rs.Handlers[pattern] = make(map[string]http.Handler)
	}
	rs.Handlers[pattern][role] = handler
}

// SelectRoute implements RouteSelector interface
func (rs *RoleBasedSelector) SelectRoute(r *http.Request, pattern string, defaultHandler http.Handler) http.Handler {
	// Extract role from request using the provided extractor
	role := rs.RoleExtractor(r)

	// If no role found, use default
	if role == "" {
		role = rs.DefaultRole
	}

	// Find handler for this pattern and role
	if rs.Handlers[pattern] != nil && rs.Handlers[pattern][role] != nil {
		return rs.Handlers[pattern][role]
	}

	return defaultHandler
}
