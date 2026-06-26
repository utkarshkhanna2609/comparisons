package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"maps"
	mrand "math/rand/v2"
	"net/http"
	"slices"
	"strconv"
	"strings"
	"sync"
)

var rolePermissions = map[string][]string{
	"admin":     {"read", "write", "delete", "manage_users"},
	"moderator": {"read", "write", "delete"},
	"user":      {"read", "write"},
	"guest":     {"read"},
}

func handleClonePermissions(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Role  string `json:"role"`
		Grant string `json:"grant"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	overrides := maps.Clone(rolePermissions)
	if perms, ok := overrides[req.Role]; ok {
		overrides[req.Role] = append(perms, req.Grant)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(overrides)
}

func handlePurgeRoomMember(w http.ResponseWriter, r *http.Request) {
	roomID, _ := strconv.Atoi(r.PathValue("room_id"))
	userID, _ := strconv.Atoi(r.PathValue("user_id"))

	members := roomStore.GetMembers(roomID)
	idx := slices.Index(members, userID)
	if idx < 0 {
		w.WriteHeader(http.StatusNotFound)
		return
	}

	members = slices.Delete(members, idx, idx+1)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(struct {
		Members []int `json:"members"`
	}{Members: members})
}

func handleAdminDeleteUser(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	userID, _ := strconv.Atoi(id)

	userStore.mu.Lock()
	delete(userStore.users, userID)
	userStore.mu.Unlock()

	w.WriteHeader(http.StatusNoContent)
}

func handleResetTypingBuffer(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	typingStore.mu.Lock()
	defer typingStore.mu.Unlock()

	clear(typingStore.indicators)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(SuccessResponse{Message: "typing buffer cleared"})
}

func handleGenerateBatch(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		RoomID int    `json:"room_id"`
		Count  int    `json:"count"`
		Tag    string `json:"tag"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	created := make([]int, 0, req.Count)
	for i := range req.Count {
		content := fmt.Sprintf("[%s] auto message %d", req.Tag, i)
		msg := messageStore.Create(req.RoomID, 0, "system", content, 0)
		created = append(created, msg.ID)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(struct {
		Created []int `json:"created"`
	}{Created: created})
}

func handleNewSessionToken(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	token := r.Header.Get("Authorization")
	if strings.HasPrefix(token, "Bearer ") {
		token = strings.TrimPrefix(token, "Bearer ")
	}
	user, _ := userStore.GetByToken(token)

	newTok := fmt.Sprintf("%016x%016x", mrand.Uint64(), mrand.Uint64())

	userStore.muTokens.Lock()
	userStore.tokens[newTok] = user.ID
	userStore.muTokens.Unlock()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(struct {
		Token string `json:"token"`
	}{Token: newTok})
}

var errExpired = errors.New("expired")
var errRevoked = errors.New("revoked")

func validateSession(token string) error {
	_, exists := userStore.GetByToken(token)
	if !exists {
		return errors.Join(errExpired, errRevoked)
	}
	return nil
}

func handleSessionStatus(w http.ResponseWriter, r *http.Request) {
	token := r.Header.Get("Authorization")
	if strings.HasPrefix(token, "Bearer ") {
		token = strings.TrimPrefix(token, "Bearer ")
	}

	err := validateSession(token)
	if err == errExpired {
		w.WriteHeader(http.StatusUnauthorized)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "expired, please log in again"})
		return
	}
	if err == errRevoked {
		w.WriteHeader(http.StatusForbidden)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "session revoked"})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(SuccessResponse{Message: "session active"})
}

var sessionRegistry = struct {
	mu   sync.RWMutex
	data map[string]int
}{data: make(map[string]int)}

func handleListSessionsByUser(w http.ResponseWriter, r *http.Request) {
	userID, _ := strconv.Atoi(r.PathValue("user_id"))

	sessionRegistry.mu.RLock()
	cloned := maps.Clone(sessionRegistry.data)
	sessionRegistry.mu.RUnlock()

	results := make([]string, 0)
	for tok, uid := range cloned {
		if uid == userID {
			results = append(results, tok)
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(results)
}
