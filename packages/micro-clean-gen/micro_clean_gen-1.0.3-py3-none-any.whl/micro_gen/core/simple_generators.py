#!/usr/bin/env python3
"""
简化版生成器 - 解决过度设计问题
"""

from pathlib import Path
from typing import Dict, Any, List
import os

class SimpleGenerator:
    """极简代码生成器"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def add_session(self):
        """添加简化的会话管理"""
        session_dir = self.project_path / "pkg" / "session"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建核心文件
        content = '''package session

import (
	"context"
	"encoding/json"
	"errors"
	"time"
)

// Session 简洁的会话结构
type Session struct {
	ID     string                 `json:"id"`
	Data   map[string]interface{} `json:"data"`
	Expiry time.Time              `json:"expiry"`
}

// NewSession 创建新会话
func NewSession(id string, ttl time.Duration) *Session {
	return &Session{
		ID:     id,
		Data:   make(map[string]interface{}),
		Expiry: time.Now().Add(ttl),
	}
}

// Store 会话存储接口
type Store interface {
	Get(ctx context.Context, id string) (*Session, error)
	Set(ctx context.Context, session *Session) error
	Delete(ctx context.Context, id string) error
}

// Manager 会话管理器
type Manager struct {
	store Store
	ttl   time.Duration
}

func NewManager(store Store, ttl time.Duration) *Manager {
	return &Manager{store: store, ttl: ttl}
}

func (m *Manager) Create(ctx context.Context, id string) (*Session, error) {
	session := NewSession(id, m.ttl)
	return session, m.store.Set(ctx, session)
}

func (m *Manager) Get(ctx context.Context, id string) (*Session, error) {
	session, err := m.store.Get(ctx, id)
	if err != nil {
		return nil, err
	}
	if time.Now().After(session.Expiry) {
		m.store.Delete(ctx, id)
		return nil, errors.New("session expired")
	}
	return session, nil
}

func (m *Manager) Delete(ctx context.Context, id string) error {
	return m.store.Delete(ctx, id)
}
'''
        
        (session_dir / "session.go").write_text(content)
        
        # 内存存储实现
        memory_store = '''package session

import (
	"context"
	"errors"
	"sync"
	"time"
)

// MemoryStore 内存存储
type MemoryStore struct {
	data map[string]*Session
	mu   sync.RWMutex
}

func NewMemoryStore() *MemoryStore {
	return &MemoryStore{
		data: make(map[string]*Session),
	}
}

func (m *MemoryStore) Get(ctx context.Context, id string) (*Session, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	session, ok := m.data[id]
	if !ok {
		return nil, errors.New("session not found")
	}
	return session, nil
}

func (m *MemoryStore) Set(ctx context.Context, session *Session) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	m.data[session.ID] = session
	return nil
}

func (m *MemoryStore) Delete(ctx context.Context, id string) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	delete(m.data, id)
	return nil
}

// 自动清理过期会话
func (m *MemoryStore) Cleanup() {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	now := time.Now()
	for id, session := range m.data {
		if now.After(session.Expiry) {
			delete(m.data, id)
		}
	}
}
'''
        
        (session_dir / "memory_store.go").write_text(memory_store)
        
        print("✅ 简化版会话管理已添加")
    
    def add_task(self):
        """添加简化的任务系统"""
        task_dir = self.project_path / "pkg" / "task"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        content = '''package task

import (
	"context"
	"encoding/json"
	"fmt"
	"time"
)

// Task 简洁的任务结构
type Task struct {
	ID      string                 `json:"id"`
	Type    string                 `json:"type"`
	Status  string                 `json:"status"`
	Payload map[string]interface{} `json:"payload"`
	Result  map[string]interface{} `json:"result,omitempty"`
	Error   string                 `json:"error,omitempty"`
	Created time.Time              `json:"created"`
	Updated time.Time              `json:"updated"`
}

func NewTask(taskType string, payload map[string]interface{}) *Task {
	now := time.Now()
	return &Task{
		ID:      fmt.Sprintf("task_%d", now.UnixNano()),
		Type:    taskType,
		Status:  "pending",
		Payload: payload,
		Created: now,
		Updated: now,
	}
}

// Store 任务存储接口
type Store interface {
	Save(ctx context.Context, task *Task) error
	Get(ctx context.Context, id string) (*Task, error)
	List(ctx context.Context, status string) ([]*Task, error)
}

// Worker 任务处理器
type Worker struct {
	store   Store
	handlers map[string]func(context.Context, map[string]interface{}) (map[string]interface{}, error)
}

func NewWorker(store Store) *Worker {
	return &Worker{
		store:    store,
		handlers: make(map[string]func(context.Context, map[string]interface{}) (map[string]interface{}, error)),
	}
}

func (w *Worker) Register(taskType string, handler func(context.Context, map[string]interface{}) (map[string]interface{}, error)) {
	w.handlers[taskType] = handler
}

func (w *Worker) Process(ctx context.Context, task *Task) error {
	handler, ok := w.handlers[task.Type]
	if !ok {
		return fmt.Errorf("no handler for task type: %s", task.Type)
	}

	task.Status = "running"
	task.Updated = time.Now()
	w.store.Save(ctx, task)

	result, err := handler(ctx, task.Payload)
	if err != nil {
		task.Status = "failed"
		task.Error = err.Error()
	} else {
		task.Status = "completed"
		task.Result = result
	}

	task.Updated = time.Now()
	return w.store.Save(ctx, task)
}
'''
        
        (task_dir / "task.go").write_text(content)
        
        print("✅ 简化版任务系统已添加")
    
    def add_saga(self):
        """添加简化的Saga事务"""
        saga_dir = self.project_path / "pkg" / "saga"
        saga_dir.mkdir(parents=True, exist_ok=True)
        
        content = '''package saga

import (
	"context"
	"fmt"
	"time"
)

// Step 事务步骤
type Step struct {
	Name      string                 `json:"name"`
	Handler   string                 `json:"handler"`
	Payload   map[string]interface{} `json:"payload"`
	Compensate string                 `json:"compensate,omitempty"`
}

// Transaction 事务
type Transaction struct {
	ID      string  `json:"id"`
	Name    string  `json:"name"`
	Steps   []Step  `json:"steps"`
	Current int     `json:"current"`
	Status  string  `json:"status"`
	Created time.Time `json:"created"`
	Updated time.Time `json:"updated"`
}

func NewTransaction(name string, steps []Step) *Transaction {
	now := time.Now()
	return &Transaction{
		ID:      fmt.Sprintf("tx_%d", now.UnixNano()),
		Name:    name,
		Steps:   steps,
		Current: 0,
		Status:  "pending",
		Created: now,
		Updated: now,
	}
}

// Store 事务存储接口
type Store interface {
	Save(ctx context.Context, tx *Transaction) error
	Get(ctx context.Context, id string) (*Transaction, error)
}

// Coordinator 事务协调器
type Coordinator struct {
	store        Store
	handlers     map[string]func(context.Context, map[string]interface{}) error
	compensators map[string]func(context.Context, map[string]interface{}) error
}

func NewCoordinator(store Store) *Coordinator {
	return &Coordinator{
		store:        store,
		handlers:     make(map[string]func(context.Context, map[string]interface{}) error),
		compensators: make(map[string]func(context.Context, map[string]interface{}) error),
	}
}

func (c *Coordinator) Register(name string, handler func(context.Context, map[string]interface{}) error, compensator func(context.Context, map[string]interface{}) error)) {
	c.handlers[name] = handler
	c.compensators[name] = compensator
}

func (c *Coordinator) Execute(ctx context.Context, tx *Transaction) error {
	tx.Status = "running"
	tx.Updated = time.Now()
	c.store.Save(ctx, tx)

	for i, step := range tx.Steps {
		handler, ok := c.handlers[step.Handler]
		if !ok {
			return fmt.Errorf("no handler for step: %s", step.Handler)
		}

		if err := handler(ctx, step.Payload); err != nil {
			tx.Status = "failed"
			tx.Current = i
			tx.Updated = time.Now()
			c.store.Save(ctx, tx)
			return c.compensate(ctx, tx)
		}

		tx.Current = i + 1
		tx.Updated = time.Now()
		c.store.Save(ctx, tx)
	}

	tx.Status = "completed"
	tx.Updated = time.Now()
	return c.store.Save(ctx, tx)
}

func (c *Coordinator) compensate(ctx context.Context, tx *Transaction) error {
	for i := tx.Current - 1; i >= 0; i-- {
		step := tx.Steps[i]
		if step.Compensate == "" {
			continue
		}

		compensator, ok := c.compensators[step.Handler]
		if ok {
			compensator(ctx, step.Payload)
		}
	}

	tx.Status = "compensated"
	tx.Updated = time.Now()
	return c.store.Save(ctx, tx)
}
'''
        
        (saga_dir / "saga.go").write_text(content)
        
        print("✅ 简化版Saga事务已添加")

# 使用示例
if __name__ == "__main__":
    generator = SimpleGenerator(Path.cwd())
    generator.add_session()
    generator.add_task()
    generator.add_saga()