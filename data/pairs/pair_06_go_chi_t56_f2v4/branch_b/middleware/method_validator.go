package middleware

import (
	"net/http"
	"strings"
)

// StandardMethods contains the standard HTTP methods as defined in RFC 9110
var StandardMethods = []string{
	http.MethodGet,
	http.MethodHead,
	http.MethodPost,
	http.MethodPut,
	http.MethodPatch,
	http.MethodDelete,
	http.MethodConnect,
	http.MethodOptions,
	http.MethodTrace,
}

// MethodValidator returns a middleware that validates the HTTP method
// against a list of allowed methods. If the method is not in the list,
// it responds with a 405 Method Not Allowed status.
func MethodValidator(allowedMethods ...string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if !isMethodAllowed(r.Method, allowedMethods) {
				w.Header().Set("Allow", strings.Join(allowedMethods, ", "))
				http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

// isMethodAllowed checks if a method is in the list of allowed methods
func isMethodAllowed(method string, allowedMethods []string) bool {
	// If no methods are specified, allow all standard methods
	if len(allowedMethods) == 0 {
		return isStandardMethod(method)
	}

	for _, m := range allowedMethods {
		if m == method {
			return true
		}
	}
	return false
}

// isStandardMethod checks if a method is one of the standard HTTP methods
func isStandardMethod(method string) bool {
	for _, m := range StandardMethods {
		if m == method {
			return true
		}
	}
	return false
}
