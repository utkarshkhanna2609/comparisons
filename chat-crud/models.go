package main

import (
	"time"
)

type User struct {
	ID           int       `json:"id"`
	Username     string    `json:"username"`
	Password     string    `json:"-"`
	Email        string    `json:"email"`
	Token        string    `json:"token,omitempty"`
	CreatedAt    time.Time `json:"created_at"`
	LastSeen     time.Time `json:"last_seen"`
	IsOnline     bool      `json:"is_online"`
	ProfilePhoto string    `json:"profile_photo,omitempty"`
}

type Room struct {
	ID        int       `json:"id"`
	Name      string    `json:"name"`
	CreatedBy int       `json:"created_by"`
	Members   []int     `json:"members"`
	IsPrivate bool      `json:"is_private"`
	CreatedAt time.Time `json:"created_at"`
}

type Message struct {
	ID          int          `json:"id"`
	RoomID      int          `json:"room_id"`
	SenderID    int          `json:"sender_id"`
	SenderName  string       `json:"sender_name"`
	Content     string       `json:"content"`
	Reactions   []Reaction   `json:"reactions"`
	Attachments []Attachment `json:"attachments,omitempty"`
	IsEdited    bool         `json:"is_edited"`
	ReplyTo     int          `json:"reply_to,omitempty"`
	CreatedAt   time.Time    `json:"created_at"`
	UpdatedAt   time.Time    `json:"updated_at"`
}

type Reaction struct {
	UserID    int    `json:"user_id"`
	Emoji     string `json:"emoji"`
	Username  string `json:"username"`
	Timestamp int64  `json:"timestamp"`
}

type Attachment struct {
	ID       int    `json:"id"`
	Filename string `json:"filename"`
	FileType string `json:"file_type"`
	Size     int64  `json:"size"`
	Data     string `json:"data"`
}

type TypingIndicator struct {
	UserID    int
	RoomID    int
	Username  string
	Timestamp time.Time
}

type ErrorResponse struct {
	Error string `json:"error"`
}

type SuccessResponse struct {
	Message string `json:"message"`
}
