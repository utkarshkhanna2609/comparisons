package main

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"sort"
	"strings"
	"sync"
	"time"
)

type UserStore struct {
	users    map[int]User
	tokens   map[string]int
	nextID   int
	mu       sync.RWMutex
	muTokens sync.RWMutex
}

type RoomStore struct {
	rooms  map[int]Room
	nextID int
	mu     sync.RWMutex
}

type MessageStore struct {
	messages map[int]Message
	nextID   int
	mu       sync.RWMutex
}

type AttachmentStore struct {
	attachments map[int]Attachment
	nextID      int
	mu          sync.RWMutex
}

type TypingStore struct {
	indicators []TypingIndicator
	mu         sync.Mutex
}

var userStore = &UserStore{
	users:  make(map[int]User),
	tokens: make(map[string]int),
	nextID: 1,
}

var roomStore = &RoomStore{
	rooms:  make(map[int]Room),
	nextID: 1,
}

var messageStore = &MessageStore{
	messages: make(map[int]Message),
	nextID:   1,
}

var attachmentStore = &AttachmentStore{
	attachments: make(map[int]Attachment),
	nextID:      1,
}

var typingStore = &TypingStore{
	indicators: make([]TypingIndicator, 0),
}

func hashPassword(password string) string {
	hash := md5.Sum([]byte(password))
	return hex.EncodeToString(hash[:])
}

func generateToken(username string) string {
	data := fmt.Sprintf("%s-%d", username, time.Now().UnixNano())
	hash := md5.Sum([]byte(data))
	return hex.EncodeToString(hash[:])
}

func (s *UserStore) Register(username, password, email string) (User, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for _, u := range s.users {
		if u.Username == username {
			return User{}, fmt.Errorf("username already exists")
		}
		if u.Email == email {
			return User{}, fmt.Errorf("email already exists")
		}
	}

	user := User{
		ID:        s.nextID,
		Username:  username,
		Password:  hashPassword(password),
		Email:     email,
		CreatedAt: time.Now(),
		LastSeen:  time.Now(),
		IsOnline:  false,
	}
	s.users[s.nextID] = user
	s.nextID++
	return user, nil
}

func (s *UserStore) Login(username, password string) (User, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for id, u := range s.users {
		if u.Username == username {
			if u.Password == hashPassword(password) {
				token := generateToken(username)
				u.Token = token
				u.IsOnline = true
				u.LastSeen = time.Now()
				s.users[id] = u

				s.muTokens.Lock()
				s.tokens[token] = id
				s.muTokens.Unlock()

				return u, nil
			} else {
				return User{}, fmt.Errorf("invalid password")
			}
		}
	}
	return User{}, fmt.Errorf("user not found")
}

func (s *UserStore) GetByToken(token string) (User, bool) {
	s.muTokens.RLock()
	userID, exists := s.tokens[token]
	s.muTokens.RUnlock()

	if !exists {
		return User{}, false
	}

	s.mu.RLock()
	user, exists := s.users[userID]
	s.mu.RUnlock()

	return user, exists
}

func (s *UserStore) Logout(token string) {
	s.muTokens.Lock()
	userID, exists := s.tokens[token]
	if exists {
		delete(s.tokens, token)
	}
	s.muTokens.Unlock()

	if exists {
		s.mu.Lock()
		if user, ok := s.users[userID]; ok {
			user.IsOnline = false
			user.Token = ""
			s.users[userID] = user
		}
		s.mu.Unlock()
	}
}

func (s *UserStore) GetByID(id int) (User, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	user, exists := s.users[id]
	return user, exists
}

func (s *UserStore) UpdateProfile(userID int, profilePhoto string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	user, exists := s.users[userID]
	if !exists {
		return fmt.Errorf("user not found")
	}

	user.ProfilePhoto = profilePhoto
	s.users[userID] = user
	return nil
}

func (s *UserStore) GetAllUsers() []User {
	s.mu.RLock()
	defer s.mu.RUnlock()

	users := make([]User, 0)
	for _, u := range s.users {
		users = append(users, u)
	}
	return users
}

func (s *RoomStore) Create(name string, createdBy int, isPrivate bool, members []int) Room {
	s.mu.Lock()
	defer s.mu.Unlock()

	allMembers := []int{createdBy}
	for _, m := range members {
		found := false
		for _, existing := range allMembers {
			if existing == m {
				found = true
				break
			}
		}
		if !found {
			allMembers = append(allMembers, m)
		}
	}

	room := Room{
		ID:        s.nextID,
		Name:      name,
		CreatedBy: createdBy,
		Members:   allMembers,
		IsPrivate: isPrivate,
		CreatedAt: time.Now(),
	}
	s.rooms[s.nextID] = room
	s.nextID++
	return room
}

func (s *RoomStore) GetByID(id int) (Room, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	room, exists := s.rooms[id]
	return room, exists
}

func (s *RoomStore) GetUserRooms(userID int) []Room {
	s.mu.RLock()
	defer s.mu.RUnlock()

	rooms := make([]Room, 0)
	for _, room := range s.rooms {
		for _, memberID := range room.Members {
			if memberID == userID {
				rooms = append(rooms, room)
				break
			}
		}
	}
	return rooms
}

func (s *RoomStore) AddMember(roomID, userID int) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	room, exists := s.rooms[roomID]
	if !exists {
		return fmt.Errorf("room not found")
	}

	for _, m := range room.Members {
		if m == userID {
			return fmt.Errorf("user already in room")
		}
	}

	room.Members = append(room.Members, userID)
	s.rooms[roomID] = room
	return nil
}

func (s *RoomStore) RemoveMember(roomID, userID int) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	room, exists := s.rooms[roomID]
	if !exists {
		return fmt.Errorf("room not found")
	}

	newMembers := make([]int, 0)
	for i := 0; i < len(room.Members); i++ {
		if room.Members[i] != userID {
			newMembers = append(newMembers, room.Members[i])
		}
	}

	if len(newMembers) == len(room.Members) {
		return fmt.Errorf("user not in room")
	}

	room.Members = newMembers
	s.rooms[roomID] = room
	return nil
}

func (s *RoomStore) Delete(roomID int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.rooms[roomID]; !exists {
		return false
	}

	delete(s.rooms, roomID)
	return true
}

func (s *MessageStore) Create(roomID, senderID int, senderName, content string, replyTo int) Message {
	s.mu.Lock()
	defer s.mu.Unlock()

	msg := Message{
		ID:          s.nextID,
		RoomID:      roomID,
		SenderID:    senderID,
		SenderName:  senderName,
		Content:     content,
		Reactions:   make([]Reaction, 0),
		Attachments: make([]Attachment, 0),
		IsEdited:    false,
		ReplyTo:     replyTo,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	s.messages[s.nextID] = msg
	s.nextID++
	return msg
}

func (s *MessageStore) GetByRoom(roomID int) []Message {
	s.mu.RLock()
	defer s.mu.RUnlock()

	messages := make([]Message, 0)
	for _, msg := range s.messages {
		if msg.RoomID == roomID {
			messages = append(messages, msg)
		}
	}

	for i := 0; i < len(messages); i++ {
		for j := i + 1; j < len(messages); j++ {
			if messages[i].CreatedAt.After(messages[j].CreatedAt) {
				temp := messages[i]
				messages[i] = messages[j]
				messages[j] = temp
			}
		}
	}

	return messages
}

func (s *MessageStore) GetByRoomPaginated(roomID, page, limit int) ([]Message, int) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	allMessages := make([]Message, 0)
	for _, msg := range s.messages {
		if msg.RoomID == roomID {
			allMessages = append(allMessages, msg)
		}
	}

	sort.Slice(allMessages, func(i, j int) bool {
		return allMessages[i].CreatedAt.Before(allMessages[j].CreatedAt)
	})

	total := len(allMessages)
	start := (page - 1) * limit
	end := start + limit

	if start >= total {
		return []Message{}, total
	}

	if end > total {
		end = total
	}

	return allMessages[start:end], total
}

func (s *MessageStore) Search(roomID int, query string) []Message {
	s.mu.RLock()
	defer s.mu.RUnlock()

	results := make([]Message, 0)
	queryLower := strings.ToLower(query)

	for _, msg := range s.messages {
		if msg.RoomID == roomID {
			if strings.Contains(strings.ToLower(msg.Content), queryLower) {
				results = append(results, msg)
			}
		}
	}

	return results
}

func (s *MessageStore) GetByID(id int) (Message, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	msg, exists := s.messages[id]
	return msg, exists
}

func (s *MessageStore) Update(id int, content string) (Message, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()

	msg, exists := s.messages[id]
	if !exists {
		return Message{}, false
	}

	msg.Content = content
	msg.IsEdited = true
	msg.UpdatedAt = time.Now()
	s.messages[id] = msg
	return msg, true
}

func (s *MessageStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.messages[id]; !exists {
		return false
	}

	delete(s.messages, id)
	return true
}

func (s *MessageStore) AddReaction(msgID int, userID int, emoji string, username string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	msg, exists := s.messages[msgID]
	if !exists {
		return fmt.Errorf("message not found")
	}

	for _, r := range msg.Reactions {
		if r.UserID == userID && r.Emoji == emoji {
			return fmt.Errorf("reaction already exists")
		}
	}

	reaction := Reaction{
		UserID:    userID,
		Emoji:     emoji,
		Username:  username,
		Timestamp: time.Now().Unix(),
	}
	msg.Reactions = append(msg.Reactions, reaction)
	s.messages[msgID] = msg
	return nil
}

func (s *MessageStore) RemoveReaction(msgID int, userID int, emoji string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	msg, exists := s.messages[msgID]
	if !exists {
		return fmt.Errorf("message not found")
	}

	newReactions := make([]Reaction, 0)
	found := false
	for _, r := range msg.Reactions {
		if r.UserID == userID && r.Emoji == emoji {
			found = true
		} else {
			newReactions = append(newReactions, r)
		}
	}

	if !found {
		return fmt.Errorf("reaction not found")
	}

	msg.Reactions = newReactions
	s.messages[msgID] = msg
	return nil
}

func (s *MessageStore) AddAttachment(msgID int, attachment Attachment) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	msg, exists := s.messages[msgID]
	if !exists {
		return fmt.Errorf("message not found")
	}

	msg.Attachments = append(msg.Attachments, attachment)
	s.messages[msgID] = msg
	return nil
}

func (s *TypingStore) SetTyping(userID, roomID int, username string) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for i, ind := range s.indicators {
		if ind.UserID == userID && ind.RoomID == roomID {
			s.indicators[i].Timestamp = time.Now()
			return
		}
	}

	s.indicators = append(s.indicators, TypingIndicator{
		UserID:    userID,
		RoomID:    roomID,
		Username:  username,
		Timestamp: time.Now(),
	})
}

func (s *TypingStore) GetTyping(roomID int) []string {
	s.mu.Lock()
	defer s.mu.Unlock()

	newIndicators := make([]TypingIndicator, 0)
	typingUsers := make([]string, 0)

	for _, ind := range s.indicators {
		if time.Since(ind.Timestamp) < 5*time.Second {
			newIndicators = append(newIndicators, ind)
			if ind.RoomID == roomID {
				typingUsers = append(typingUsers, ind.Username)
			}
		}
	}

	s.indicators = newIndicators
	return typingUsers
}
