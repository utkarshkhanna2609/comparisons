package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	if _, err := os.Stat("uploads"); os.IsNotExist(err) {
		os.Mkdir("uploads", 0755)
	}

	http.HandleFunc("/register", handleRegister)
	http.HandleFunc("/login", handleLogin)
	http.HandleFunc("/logout", authMiddleware(handleLogout))
	http.HandleFunc("/users", authMiddleware(handleGetUsers))
	http.HandleFunc("/profile", authMiddleware(handleUpdateProfile))

	http.HandleFunc("/rooms", authMiddleware(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			handleCreateRoom(w, r)
		} else if r.Method == http.MethodGet {
			handleGetRooms(w, r)
		} else {
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	}))
	http.HandleFunc("/room/delete", authMiddleware(handleDeleteRoom))
	http.HandleFunc("/room/members", authMiddleware(handleRoomMembers))

	http.HandleFunc("/messages", authMiddleware(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			handleCreateMessage(w, r)
		} else if r.Method == http.MethodGet {
			handleGetMessages(w, r)
		} else {
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	}))
	http.HandleFunc("/messages/search", authMiddleware(handleSearchMessages))
	http.HandleFunc("/message", authMiddleware(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPut {
			handleUpdateMessage(w, r)
		} else if r.Method == http.MethodDelete {
			handleDeleteMessage(w, r)
		} else {
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	}))

	http.HandleFunc("/reaction", authMiddleware(handleReaction))
	http.HandleFunc("/typing", authMiddleware(handleTyping))
	http.HandleFunc("/attachment", authMiddleware(handleUploadAttachment))

	fmt.Println("Server starting on :8080...")
	http.ListenAndServe(":8080", nil)
}
