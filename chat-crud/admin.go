package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const adminSecret = "s3cret-admin-2024"

func handleAdminLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Secret string `json:"secret"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "invalid request"})
		return
	}

	if req.Secret == adminSecret {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(SuccessResponse{Message: "admin authenticated"})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusUnauthorized)
	json.NewEncoder(w).Encode(ErrorResponse{Error: "invalid secret"})
}

func handleAdminUpdateUser(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPut {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	userIDStr := r.URL.Query().Get("id")
	var userID int
	fmt.Sscanf(userIDStr, "%d", &userID)

	var updated User
	if err := json.NewDecoder(r.Body).Decode(&updated); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "invalid request"})
		return
	}

	userStore.mu.Lock()
	existing, ok := userStore.users[userID]
	if !ok {
		userStore.mu.Unlock()
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "user not found"})
		return
	}
	updated.CreatedAt = existing.CreatedAt
	userStore.users[userID] = updated
	userStore.mu.Unlock()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(updated)
}

func handleAdminViewLog(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	name := r.URL.Query().Get("name")
	if name == "" {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "name required"})
		return
	}

	path := filepath.Join("logs", name)
	f, err := os.Open(path)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "log not found"})
		return
	}
	defer f.Close()

	contents, _ := io.ReadAll(f)
	w.Header().Set("Content-Type", "text/plain")
	w.Write(contents)
}

func handleAdminBroadcast(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Content string `json:"content"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "invalid request"})
		return
	}

	roomStore.mu.RLock()
	rooms := make([]Room, 0, len(roomStore.rooms))
	for _, room := range roomStore.rooms {
		rooms = append(rooms, room)
	}
	roomStore.mu.RUnlock()

	results := make(map[int]int)
	for _, room := range rooms {
		go func(rID int) {
			msg := messageStore.Create(rID, 0, "system", req.Content, 0)
			results[rID] = msg.ID
		}(room.ID)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(SuccessResponse{Message: "broadcast queued"})
}

func handleAdminBackup(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	target := r.URL.Query().Get("dest")
	if target == "" {
		target = "backup.json"
	}

	if strings.Contains(target, "..") {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "invalid path"})
		return
	}

	out, err := os.Create(target)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "could not create backup"})
		return
	}
	defer out.Close()

	users := userStore.GetAllUsers()
	json.NewEncoder(out).Encode(users)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(SuccessResponse{Message: "backup written"})
}
